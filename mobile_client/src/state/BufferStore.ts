export type BufferName = "all" | "chat" | "game" | "system" | "misc";

export type BufferItem = {
  id: string;
  buffer: BufferName;
  text: string;
  timestamp: number;
};

export class BufferStore {
  private readonly buffers = new Map<BufferName, BufferItem[]>();
  private readonly muted = new Set<BufferName>();
  private nextId = 0;

  constructor(private readonly maxItemsPerBuffer = 500) {
    if (!Number.isSafeInteger(maxItemsPerBuffer) || maxItemsPerBuffer < 1) {
      throw new RangeError("Buffer capacity must be a positive integer");
    }
    (["all", "chat", "game", "system", "misc"] as const).forEach((buffer) => {
      this.buffers.set(buffer, []);
    });
  }

  add(buffer: BufferName, text: string): void {
    const item: BufferItem = {
      id: `message:${++this.nextId}`,
      buffer,
      text,
      timestamp: Date.now(),
    };
    this.append(buffer, item);
    if (buffer !== "all") {
      this.append("all", item);
    }
  }

  private append(buffer: BufferName, item: BufferItem): void {
    const messages = this.buffers.get(buffer);
    if (!messages) return;
    messages.push(item);
    if (messages.length > this.maxItemsPerBuffer) {
      messages.splice(0, messages.length - this.maxItemsPerBuffer);
    }
  }

  clear(): void {
    this.buffers.forEach((messages) => { messages.length = 0; });
  }

  getMessages(buffer: BufferName): BufferItem[] {
    return [...(this.buffers.get(buffer) ?? [])];
  }

  isMuted(buffer: BufferName): boolean {
    return this.muted.has(buffer);
  }
}
