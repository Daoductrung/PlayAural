import type { SpeechBuffer } from "../network/packets";

export const BUFFER_NAMES = ["all", "chat", "private", "game", "system", "misc"] as const satisfies readonly SpeechBuffer[];
export type BufferName = SpeechBuffer;

export function normalizeBufferName(buffer: unknown): BufferName {
  if (buffer === "chats") {
    return "chat";
  }
  return BUFFER_NAMES.includes(buffer as BufferName) ? buffer as BufferName : "misc";
}

export type BufferItem = {
  id: string;
  sequence: number;
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
    BUFFER_NAMES.forEach((buffer) => {
      this.buffers.set(buffer, []);
    });
  }

  add(buffer: BufferName | string, text: string): void {
    const normalizedBuffer = normalizeBufferName(buffer);
    const sequence = ++this.nextId;
    const item: BufferItem = {
      id: `message:${sequence}`,
      sequence,
      buffer: normalizedBuffer,
      text,
      timestamp: Date.now(),
    };
    this.append(normalizedBuffer, item);
    if (normalizedBuffer !== "all" && !this.isDirectlyMuted(normalizedBuffer)) {
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

  private mergeSourcesIntoAll(sourceBuffers: Iterable<BufferName>): void {
    const allMessages = this.buffers.get("all");
    if (!allMessages) return;

    const itemsById = new Map(allMessages.map((item) => [item.id, item]));
    for (const sourceBuffer of sourceBuffers) {
      if (sourceBuffer === "all") continue;
      for (const item of this.buffers.get(sourceBuffer) ?? []) {
        itemsById.set(item.id, item);
      }
    }
    const merged = [...itemsById.values()]
      .sort((left, right) => left.sequence - right.sequence)
      .slice(-this.maxItemsPerBuffer);
    allMessages.splice(0, allMessages.length, ...merged);
  }

  clear(): void {
    this.buffers.forEach((messages) => { messages.length = 0; });
  }

  getMessages(buffer: BufferName): BufferItem[] {
    return [...(this.buffers.get(buffer) ?? [])];
  }

  getVisibleMessages(buffer: BufferName): BufferItem[] {
    return this.isMuted(buffer) ? [] : this.getMessages(buffer);
  }

  getMutedBuffers(): BufferName[] {
    return BUFFER_NAMES.filter((buffer) => this.muted.has(buffer));
  }

  setMutedBuffers(buffers: unknown): boolean {
    const next = new Set<BufferName>();
    if (Array.isArray(buffers)) {
      buffers.forEach((buffer) => {
        const normalized = normalizeBufferName(buffer);
        if (buffer === "chats" || BUFFER_NAMES.includes(buffer as BufferName)) {
          next.add(normalized);
        }
      });
    }
    const previouslyMuted = new Set(this.muted);
    const changed = next.size !== previouslyMuted.size
      || [...next].some((buffer) => !this.muted.has(buffer));
    if (changed) {
      this.muted.clear();
      next.forEach((buffer) => this.muted.add(buffer));
      this.mergeSourcesIntoAll(
        [...previouslyMuted].filter((buffer) => !next.has(buffer)),
      );
    }
    return changed;
  }

  isDirectlyMuted(buffer: BufferName): boolean {
    return this.muted.has(buffer);
  }

  isMuted(buffer: BufferName): boolean {
    return this.muted.has("all") || this.muted.has(buffer);
  }
}
