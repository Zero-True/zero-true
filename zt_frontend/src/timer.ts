export class Timer {
    private timerId: number | null = null;
    private readonly duration: number;
  
    constructor(duration: number) {
      this.duration = duration;
    }
  
    start(callback: () => void): void {
      if (this.timerId === null) {
        this.timerId = window.setTimeout(() => {
          callback();
          this.timerId = null;
        }, this.duration);
      }
    }
  
    stop(): void {
      if (this.timerId !== null) {
        clearTimeout(this.timerId);
        this.timerId = null;
      }
    }
  }