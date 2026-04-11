export type BufferName = "all" | "chat" | "game" | "system" | "misc";

export type BufferItem = {
  buffer: BufferName;
  text: string;
  timestamp: number;
};

export class BufferStore {
  private readonly buffers = new Map<BufferName, BufferItem[]>();
  private readonly muted = new Set<BufferName>();

  constructor() {
    (["all", "chat", "game", "system", "misc"] as const).forEach((buffer) => {
      this.buffers.set(buffer, []);
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

  isMuted(buffer: BufferName): boolean {
    return this.muted.has(buffer);
  }
}
