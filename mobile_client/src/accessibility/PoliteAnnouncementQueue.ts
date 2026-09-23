export type AnnouncementFrameScheduler = {
  cancel(handle: number): void;
  request(callback: () => void): number;
};

export class PoliteAnnouncementQueue {
  private disposed = false;
  private frame: number | null = null;
  private hasPublishedContent = false;
  private readonly pending: string[] = [];

  constructor(
    private readonly publish: (text: string) => void,
    private readonly capacity: number,
    private readonly scheduler: AnnouncementFrameScheduler = {
      cancel: (handle) => cancelAnimationFrame(handle),
      request: (callback) => requestAnimationFrame(callback),
    },
  ) {
    if (!Number.isSafeInteger(capacity) || capacity < 1) {
      throw new RangeError("Announcement capacity must be a positive integer");
    }
  }

  enqueue(text: string, options: { interrupt?: boolean } = {}): void {
    if (this.disposed || !text) return;
    if (options.interrupt) this.clear();
    this.pending.push(text);
    if (this.pending.length > this.capacity) {
      this.pending.splice(0, this.pending.length - this.capacity);
    }
    this.schedule();
  }

  clear(): void {
    if (this.disposed) return;
    this.pending.length = 0;
    if (this.frame !== null) {
      this.scheduler.cancel(this.frame);
      this.frame = null;
    }
    if (this.hasPublishedContent) {
      this.hasPublishedContent = false;
      this.publish("");
    }
  }

  dispose(): void {
    if (this.frame !== null) this.scheduler.cancel(this.frame);
    this.frame = null;
    this.pending.length = 0;
    this.disposed = true;
  }

  private schedule(): void {
    if (this.frame !== null || this.pending.length === 0) return;
    this.frame = this.scheduler.request(() => {
      this.frame = null;
      const next = this.pending.shift();
      if (next !== undefined) {
        this.hasPublishedContent = true;
        this.publish(next);
      }
      this.schedule();
    });
  }
}
