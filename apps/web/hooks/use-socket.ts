import { useEffect } from 'react';
import { socketManager } from '@/libs/socket';
import { useOrgStore } from '@/store/org-store';
import { useSocketStore } from '@/store/socket-store';
import { useBearerToken } from './use-bearer-token';

export const useSocket = () => {
  const { getToken } = useBearerToken();
  const { isConnected, error, setError, setIsConnected, roomId, setRoomId } = useSocketStore();
  const { selectedOrg } = useOrgStore();
  useEffect(() => {
    let mounted = true;

    const connect = async () => {
      try {
        if (!selectedOrg?.id) {
          return;
        }
        if (isConnected) socketManager.disconnect();
        await socketManager.connect(getToken, selectedOrg?.id);
        if (mounted) {
          setIsConnected(true);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Connection failed');
          setIsConnected(false);
        }
      }
    };

    connect();

    // Listen to connection events
    const handleConnect = () => {
      if (mounted) setIsConnected(true);
      if (roomId && selectedOrg?.id) {
        socketManager.joinRoom(selectedOrg.id);
      }
    };

    const handleDisconnect = () => {
      if (mounted) setIsConnected(false);
    };

    socketManager.on('connect', handleConnect);
    socketManager.on('disconnect', handleDisconnect);

    return () => {
      mounted = false;
      socketManager.off('connect', handleConnect);
      socketManager.off('disconnect', handleDisconnect);
    };
  }, [getToken, setError, setIsConnected, selectedOrg?.id, roomId, setRoomId, isConnected]);

  const emit = <T>(event: string, data?: T) => {
    socketManager.emit(event, data);
  };

  const on = <T>(event: string, callback: (data: T) => void) => {
    socketManager.on(event, callback);
  };

  const off = <T>(event: string, callback?: (data: T) => void) => {
    socketManager.off(event, callback);
  };

  return {
    isConnected,
    error,
    emit,
    on,
    off,
    socket: socketManager,
  };
};
