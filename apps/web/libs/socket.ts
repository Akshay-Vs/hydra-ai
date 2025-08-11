import { io } from 'socket.io-client';

const URL = process.env.SOCKET_URL ?? 'http://localhost:8000';

export const socket = io(URL, {
  autoConnect: true,
  timeout: 5000,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  transports: ['websocket'],
});
