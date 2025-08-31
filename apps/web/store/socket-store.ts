import { create } from 'zustand';

type SocketStore = {
  isConnected: boolean;
  setIsConnected: (connected: boolean) => void;

  isConnecting: boolean;
  setIsConnecting: (connecting: boolean) => void;

  roomId?: string;
  setRoomId?: (roomId: string) => void;

  error: string | null;
  setError: (error: string | null) => void;
};

export const useSocketStore = create<SocketStore>(set => ({
  isConnected: false,
  setIsConnected: (connected: boolean) => set({ isConnected: connected }),

  isConnecting: false,
  setIsConnecting: (connecting: boolean) => set({ isConnecting: connecting }),

  roomId: undefined,
  setRoomId: (roomId: string) => set({ roomId }),

  error: null,
  setError: (error: string | null) => set({ error }),
}));
