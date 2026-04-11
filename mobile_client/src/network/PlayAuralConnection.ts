import type { ClientPacket, ServerPacket } from "./packets";

type ConnectionHandlers = {
  onClose?: (reason?: string) => void;
  onError?: (message: string) => void;
  onOpen?: () => void;
  onPacket: (packet: ServerPacket) => void;
};

export class PlayAuralConnection {
  private socket: WebSocket | null = null;
  private intentionallyClosingSocket: WebSocket | null = null;

  constructor(private readonly handlers: ConnectionHandlers) {}

  connect(serverUrl: string, username: string, password: string, version: string): void {
    this.disconnect();
    this.intentionallyClosingSocket = null;

    const socket = new WebSocket(serverUrl);
    this.socket = socket;

    socket.onopen = () => {
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
      try {
        const packet = JSON.parse(String(event.data)) as ServerPacket;
        this.handlers.onPacket(packet);
      } catch {
        this.handlers.onError?.("Malformed server packet.");
      }
    };

    socket.onerror = () => {
      this.handlers.onError?.("Connection error.");
    };

    socket.onclose = (event) => {
      const wasIntentional = this.intentionallyClosingSocket === socket;
      if (wasIntentional) {
        this.intentionallyClosingSocket = null;
      }
      if (this.socket === socket) {
        this.socket = null;
      }
      if (wasIntentional) {
        return;
      }
      this.handlers.onClose?.(event.reason || undefined);
    };
  }

  disconnect(): void {
    if (!this.socket) {
      return;
    }
    this.intentionallyClosingSocket = this.socket;
    this.socket.close();
    this.socket = null;
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
}
