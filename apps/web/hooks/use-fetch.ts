// useFetch.ts
import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import type { AxiosRequestConfig } from 'axios';
import { api } from '@/libs/api';

export const useFetch = <TData = unknown,>(
  key: string | unknown[],
  url: string,
  config?: AxiosRequestConfig,
  options?: Omit<UseQueryOptions<TData>, 'queryKey' | 'queryFn'>
) => {
  const { getToken } = useAuth();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    getToken().then(setToken);
  }, [getToken]);

  return useQuery<TData>({
    queryKey: [...(Array.isArray(key) ? key : [key]), token],
    queryFn: async () => {
      if (!token) throw new Error('No token available');
      const res = await api.request<TData>({
        url,
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
        ...config,
      });
      return res.data;
    },
    enabled: !!token,
    ...options,
  });
};
