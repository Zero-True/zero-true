type WebSocketOptions = {
  onOpen?: () => void;
  onMessage?: (message: any) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (error: Event) => void;
  pingInterval?: number;
  reconnectDelay?: number;
};

import { globalState } from "@/global_vars";

export class WebSocketManager {
  private socket: WebSocket | undefined;
  private pingInterval: number | undefined;
  private pingTimeout: number | undefined;
  private url: string;
  private options: WebSocketOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private connected = false;

  constructor(url: string, options: WebSocketOptions = {}) {
    this.url = url;
    this.options = options;
  }

  public initializeSocket() {
    this.socket = new WebSocket(this.url);

    this.socket.onclose = (event) => {
      console.log(
        `WebSocket closed: ${this.url}, Code: ${event.code}, Reason: ${event.reason}`
      );
      this.stopPing();
      this.options.onClose?.(event);
      if (this.connected) {
        this.reconnectSocket();
        this.connected = false;
      }
    };

    this.socket.onmessage = (event: any) => {
      if (event.data === "pong") {
        clearTimeout(this.pingTimeout);
      } else {
        this.options.onMessage?.(event);
      }
    };
    return new Promise((resolve, reject) => {
      this.socket!.onopen = () => {
        console.log(`WebSocket connected: ${this.url}`);
        this.connected = true;
        this.startPing();
        this.options.onOpen?.();
        resolve("");
      };

      this.socket!.onerror = (error) => {
        console.error(`WebSocket error: ${this.url}`, error);
        this.options.onError?.(error);
        reject(error);
      };
    });
  }

  private startPing() {
    const interval = this.options.pingInterval || 30000;
    this.pingInterval = window.setInterval(() => {
      if (this.socket!.readyState === WebSocket.OPEN) {
        this.socket!.send(JSON.stringify({ type: "ping" }));
        this.pingTimeout = window.setTimeout(() => {
          console.log(`Ping timeout: ${this.url}`);
          this.socket!.close();
        }, 5000);
      }
    }, interval);
  }

  private stopPing() {
    clearInterval(this.pingInterval);
    clearTimeout(this.pingTimeout);
  }

  private reconnectSocket() {
    const delay = this.options.reconnectDelay || 2000;

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      console.log(
        `Reconnecting WebSocket: ${this.url} (Attempt ${
          this.reconnectAttempts + 1
        }/${this.maxReconnectAttempts})`
      );

      setTimeout(async () => {
        try {
          await this.initializeSocket();
          this.reconnectAttempts = 0;
          console.log(`WebSocket reconnected successfully: ${this.url}`);
        } catch (error) {
          console.error(
            `Reconnect attempt failed for WebSocket: ${this.url}`,
            error
          );
          this.reconnectAttempts++;
          this.reconnectSocket();
        }
      }, delay);
    } else {
      console.error(
        `Max reconnect attempts reached for WebSocket: ${this.url}. Giving up.`
      );
      globalState.connection_lost = true;
    }
  }

  public send(data: any) {
    if (this.socket!.readyState === WebSocket.OPEN) {
      this.socket!.send(data);
    } else {
      console.warn(`WebSocket not open: ${this.url}`);
    }
  }

  public close() {
    this.stopPing();
    this.socket!.close();
  }
}
