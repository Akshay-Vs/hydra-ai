import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';

export const useBearerToken = () => {
  const { getToken, isLoaded } = useAuth();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    getToken().then(setToken);
  }, [getToken, setToken]);

  return { token, isLoaded, getToken };
};
