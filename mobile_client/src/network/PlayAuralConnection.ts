import type { ClientPacket, ServerPacket } from "./packets";

type ConnectionHandlers = {
  onClose?: (reason?: string) => void;
  onError?: (message: string) => void;
  onOpen?: () => void;
  onPacket: (packet: ServerPacket) => void;
};

export class PlayAuralConnection {
  private socket: WebSocket | null = null;
  private readonly intentionallyClosingSockets = new Set<WebSocket>();
  private readonly closeWaiters = new Map<WebSocket, Set<() => void>>();

  constructor(private readonly handlers: ConnectionHandlers) {}

  connect(serverUrl: string, username: string, password: string, version: string): void {
    this.disconnect();

    const socket = new WebSocket(serverUrl);
    this.socket = socket;

    socket.onopen = () => {
      if (this.socket !== socket) {
        return;
      }
      this.handlers.onOpen?.();
      this.send({
        client: "mobile",
        password,
        type: "authorize",
        username,
        version,
      });
    };

    socket.onmessage = (event) => {
      if (this.socket !== socket) {
        return;
      }
      try {
        const packet = JSON.parse(String(event.data)) as ServerPacket;
        this.handlers.onPacket(packet);
      } catch {
        this.handlers.onError?.("Malformed server packet.");
      }
    };

    socket.onerror = () => {
      if (this.socket !== socket || this.intentionallyClosingSockets.has(socket)) {
        return;
      }
      this.handlers.onError?.("Connection error.");
    };

    socket.onclose = (event) => {
      const wasIntentional = this.intentionallyClosingSockets.delete(socket);
      const wasActive = this.socket === socket;
      if (wasActive) {
        this.socket = null;
      }
      this.resolveCloseWaiters(socket);
      if (wasIntentional || !wasActive) {
        return;
      }
      this.handlers.onClose?.(event.reason || undefined);
    };
  }

  disconnect(): void {
    this.closeSocket(this.socket);
  }

  disconnectAndWait(timeoutMs = 1500): Promise<void> {
    const socket = this.socket;
    if (!socket) {
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      let settled = false;
      const finish = () => {
        if (settled) {
          return;
        }
        settled = true;
        clearTimeout(timeoutHandle);
        const waiters = this.closeWaiters.get(socket);
        if (waiters) {
          waiters.delete(finish);
          if (waiters.size === 0) {
            this.closeWaiters.delete(socket);
          }
        }
        resolve();
      };
      const timeoutHandle = setTimeout(finish, timeoutMs);
      this.addCloseWaiter(socket, finish);
      this.closeSocket(socket);
      if (socket.readyState === WebSocket.CLOSED) {
        finish();
      }
    });
  }

  send(packet: ClientPacket): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return;
    }
    this.socket.send(JSON.stringify(packet));
  }

  requestTemporary(
    serverUrl: string,
    packet: ClientPacket,
    responseTypes: string[],
    timeoutMs = 12000,
  ): Promise<ServerPacket> {
    return new Promise((resolve, reject) => {
      let settled = false;
      const socket = new WebSocket(serverUrl);

      const finish = (callback: () => void) => {
        if (settled) {
          return;
        }
        settled = true;
        clearTimeout(timeoutHandle);
        try {
          socket.close();
        } catch {
          // Ignore close failures on temporary auth sockets.
        }
        callback();
      };

      const timeoutHandle = setTimeout(() => {
        finish(() => reject(new Error("Temporary request timed out.")));
      }, timeoutMs);

      socket.onopen = () => {
        socket.send(JSON.stringify(packet));
      };

      socket.onmessage = (event) => {
        try {
          const response = JSON.parse(String(event.data)) as ServerPacket;
          if (responseTypes.includes(response.type)) {
            finish(() => resolve(response));
          }
        } catch {
          finish(() => reject(new Error("Malformed server packet.")));
        }
      };

      socket.onerror = () => {
        finish(() => reject(new Error("Connection error.")));
      };

      socket.onclose = (event) => {
        if (!settled) {
          finish(() => reject(new Error(event.reason || "Connection closed.")));
        }
      };
    });
  }

  private addCloseWaiter(socket: WebSocket, waiter: () => void): void {
    const existing = this.closeWaiters.get(socket);
    if (existing) {
      existing.add(waiter);
      return;
    }
    this.closeWaiters.set(socket, new Set([waiter]));
  }

  private resolveCloseWaiters(socket: WebSocket): void {
    const waiters = this.closeWaiters.get(socket);
    if (!waiters) {
      return;
    }
    this.closeWaiters.delete(socket);
    for (const waiter of waiters) {
      waiter();
    }
  }

  private closeSocket(socket: WebSocket | null): void {
    if (!socket) {
      return;
    }
    this.intentionallyClosingSockets.add(socket);
    if (this.socket === socket) {
      this.socket = null;
    }
    if (socket.readyState === WebSocket.CLOSED) {
      this.intentionallyClosingSockets.delete(socket);
      this.resolveCloseWaiters(socket);
      return;
    }
    try {
      socket.close();
    } catch {
      this.intentionallyClosingSockets.delete(socket);
      this.resolveCloseWaiters(socket);
    }
  }
}
