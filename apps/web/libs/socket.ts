// utils/socket.ts
import { warn } from 'console';
import type { Socket } from 'socket.io-client';
import { io } from 'socket.io-client';

export type EventCallback<T> = (data: T) => void;
export type EventCallbackWithAck<T = unknown> = (
  data: T,
  ack?: (response: unknown) => void
) => void;

export interface SocketConfig {
  url?: string;
  timeout?: number;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  transports?: ('websocket' | 'polling')[];
  autoConnect?: boolean;
}

class SocketManager {
  private socket: Socket | null = null;
  private eventListeners: Map<string, EventCallback<unknown>[]> = new Map();
  private config: Required<SocketConfig>;
  private getTokenFn: (() => Promise<string | null>) | null = null;

  constructor(config: SocketConfig = {}) {
    this.config = {
      url: config.url ?? process.env.NEXT_PUBLIC_SOCKET_URL ?? 'http://localhost:8000',
      timeout: config.timeout ?? 10000,
      reconnectionAttempts: config.reconnectionAttempts ?? 5,
      reconnectionDelay: config.reconnectionDelay ?? 1000,
      transports: config.transports ?? ['websocket', 'polling'],
      autoConnect: config.autoConnect ?? true,
    };
  }

  async connect(
    getToken: () => Promise<string | null>,
    org_id?: string,
    additionalAuth: Record<string, unknown> = {}
  ): Promise<Socket> {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.getTokenFn = getToken;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      // Disconnect existing socket if any
      if (this.socket) {
        this.socket.disconnect();
      }

      this.socket = io(this.config.url, {
        auth: {
          token,
          org_id,
          ...additionalAuth,
        },
        transports: this.config.transports,
        timeout: this.config.timeout,
        reconnection: true,
        reconnectionAttempts: this.config.reconnectionAttempts,
        reconnectionDelay: this.config.reconnectionDelay,
        autoConnect: this.config.autoConnect,
      });

      // Set up core event listeners
      this.setupCoreEventListeners();

      // Re-register all custom event listeners
      this.reregisterEventListeners();

      return new Promise((resolve, reject) => {
        if (!this.socket) return reject(new Error('Socket not initialized'));

        const connectHandler = () => {
          console.log('Connected to Socket.IO server');
          if (this.socket) {
            resolve(this.socket);
          }
        };

        const errorHandler = (error: Error) => {
          console.error('Socket.IO connection error:', error);
          reject(error);
        };

        this.socket.once('connect', connectHandler);
        this.socket.once('connect_error', errorHandler);

        // Handle initial connection timeout
        setTimeout(() => {
          if (!this.socket?.connected) {
            this.socket?.off('connect', connectHandler);
            this.socket?.off('connect_error', errorHandler);
            reject(new Error('Connection timeout'));
          }
        }, this.config.timeout);
      });
    } catch (error) {
      console.error('Failed to connect to socket:', error);
      throw error;
    }
  }

  private setupCoreEventListeners() {
    if (!this.socket) return;

    this.socket.on('disconnect', reason => {
      console.log('Disconnected from server:', reason);
    });

    // Handle reconnection with fresh token
    this.socket.on('reconnect_attempt', async () => {
      console.log('Attempting to reconnect...');
      try {
        if (this.getTokenFn) {
          const token = await this.getTokenFn();
          if (token && this.socket) {
            this.socket.auth = { ...this.socket.auth, token };
          }
        }
      } catch (error) {
        console.error('Failed to refresh token for reconnection:', error);
      }
    });

    this.socket.on('reconnect', () => {
      console.log('Successfully reconnected to server');
    });

    this.socket.on('reconnect_failed', () => {
      console.error('Failed to reconnect after maximum attempts');
    });
  }

  private reregisterEventListeners() {
    if (!this.socket) return;

    this.eventListeners.forEach((callbacks, event) => {
      callbacks.forEach(callback => {
        if (this.socket) {
          this.socket.on(event, callback);
        }
      });
    });
  }

  // Generic emit method for any event
  emit<T = unknown>(event: string, data?: T): void {
    if (!this.socket?.connected) {
      throw new Error('Socket not connected');
    }
    this.socket.emit(event, data);
  }

  // Generic emit with acknowledgment
  emitWithAck<T = unknown, R = unknown>(event: string, data?: T): Promise<R> {
    return new Promise((resolve, reject) => {
      if (!this.socket?.connected) {
        reject(new Error('Socket not connected'));
        return;
      }

      this.socket.emit(event, data, (response: R) => {
        resolve(response);
      });
    });
  }

  // Generic event listener
  on<T = unknown>(event: string, callback: EventCallback<T>): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }

    const listeners = this.eventListeners.get(event);
    if (listeners) {
      // Type assertion is safe here since we're storing all callbacks as EventCallback<unknown>
      listeners.push(callback as EventCallback<unknown>);
    }

    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  // Listen to event only once
  once<T = unknown>(event: string, callback: EventCallback<T>): void {
    if (this.socket) {
      this.socket.once(event, callback);
    }
  }

  // Remove event listener
  off<T = unknown>(event: string, callback?: EventCallback<T>): void {
    if (callback) {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        const index = listeners.indexOf(callback as EventCallback<unknown>);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }

      if (this.socket) {
        this.socket.off(event, callback);
      }
    } else {
      // Remove all listeners for the event
      this.eventListeners.delete(event);
      if (this.socket) {
        this.socket.off(event);
      }
    }
  }

  // Remove all event listeners
  removeAllListeners(event?: string): void {
    if (event) {
      this.eventListeners.delete(event);
      if (this.socket) {
        this.socket.removeAllListeners(event);
      }
    } else {
      this.eventListeners.clear();
      if (this.socket) {
        this.socket.removeAllListeners();
        // Re-setup core listeners
        this.setupCoreEventListeners();
      }
    }
  }

  // Join a room
  joinRoom(room: string): void {
    this.emit('join_room', { room });
  }

  // Leave a room
  leaveRoom(room: string): void {
    this.emit('leave_room', { room });
  }

  // Emit to a specific room
  emitToRoom<T = unknown>(room: string, event: string, data?: T): void {
    this.emit('room_message', { room, event, data });
  }

  // Disconnect from server
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.eventListeners.clear();
    this.getTokenFn = null;
  }

  // Get connection status
  get connected(): boolean {
    return this.socket?.connected ?? false;
  }

  // Get the raw socket instance (use with caution)
  get socketInstance(): Socket | null {
    return this.socket;
  }

  // Get socket ID
  get id(): string | undefined {
    return this.socket?.id;
  }

  // Update socket configuration
  updateConfig(config: Partial<SocketConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Export a default instance
export const socketManager = new SocketManager();

// Export the class for creating multiple instances
export { SocketManager };
