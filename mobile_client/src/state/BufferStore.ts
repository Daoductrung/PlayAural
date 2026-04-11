export type BufferName = "all" | "chat" | "game" | "system" | "misc";

export type BufferItem = {
  buffer: BufferName;
  text: string;
  timestamp: number;
};

export class BufferStore {
  private readonly buffers = new Map<BufferName, BufferItem[]>();
  private readonly positions = new Map<BufferName, number>();
  private readonly muted = new Set<BufferName>();

  constructor() {
    (["all", "chat", "game", "system", "misc"] as const).forEach((buffer) => {
      this.buffers.set(buffer, []);
      this.positions.set(buffer, 0);
    });
  }

  add(buffer: BufferName, text: string): void {
    const item: BufferItem = {
      buffer,
      text,
      timestamp: Date.now(),
    };
    this.buffers.get(buffer)?.push(item);
    if (buffer !== "all") {
      this.buffers.get("all")?.push(item);
    }
  }

  getMessages(buffer: BufferName): BufferItem[] {
    return [...(this.buffers.get(buffer) ?? [])];
  }

  getCurrent(buffer: BufferName): BufferItem | null {
    const items = this.buffers.get(buffer) ?? [];
    if (items.length === 0) {
      return null;
    }
    const position = this.positions.get(buffer) ?? 0;
    const index = Math.max(0, items.length - 1 - position);
    return items[index] ?? null;
  }

  move(buffer: BufferName, direction: "older" | "newer" | "oldest" | "newest"): BufferItem | null {
    const items = this.buffers.get(buffer) ?? [];
    if (items.length === 0) {
      return null;
    }
    const current = this.positions.get(buffer) ?? 0;
    let next = current;
    if (direction === "older") {
      next = Math.min(items.length - 1, current + 1);
    } else if (direction === "newer") {
      next = Math.max(0, current - 1);
    } else if (direction === "oldest") {
      next = items.length - 1;
    } else if (direction === "newest") {
      next = 0;
    }
    this.positions.set(buffer, next);
    return this.getCurrent(buffer);
  }

  isMuted(buffer: BufferName): boolean {
    return this.muted.has(buffer);
  }
}
