import { useCallback, useMemo, useRef } from 'react';
import { useAuth } from '@clerk/nextjs';
import type { UseMutationOptions, UseMutationResult } from '@tanstack/react-query';
import { useMutation } from '@tanstack/react-query';
import type { AxiosRequestConfig, AxiosError } from 'axios';
import { api } from '@/libs/api';

type MutationFnArgs = {
  url: string;
  method?: AxiosRequestConfig['method'];
  data?: unknown;
  config?: AxiosRequestConfig;
};

export const useMutate = <TData = unknown, TError = unknown, TContext = unknown>(
  options?: Omit<UseMutationOptions<TData, TError, MutationFnArgs, TContext>, 'mutationFn'>
): UseMutationResult<TData, TError, MutationFnArgs, TContext> & {
  lastSuccessData: TData | undefined;
} => {
  /**
   * A custom React hook that wraps TanStack Query's
   * useMutation with enhanced API request capabilities.
   * Automatically handles authentication tokens,
   * provides better error handling, and persists last successful response data.
   *
   * @param {Object} options - TanStack Query mutation options (excluding mutationFn)
   * @param {Function} [options.onSuccess] - Callback fired on successful mutation
   * @param {Function} [options.onError] - Callback fired on failed mutation
   * @param {Function} [options.onSettled] - Callback fired when mutation settles (success or error)
   * @param {Function} [options.onMutate] - Callback fired before mutation starts
   * @param {boolean} [options.retry] - Whether to retry failed mutations
   *
   * @example
   * ```tsx
   * const { mutate, isPending, lastSuccessData, error } = useMutate<User>({
   *   onSuccess: (user) => console.log('User created:', user.name),
   *   onError: (error) => toast.error(error.message),
   *   onMutate: async (variables) => {
   *     // Optimistic update logic here
   *     return { previousData: 'snapshot' };
   *   }
   * });
   *
   * const handleCreateUser = () => {
   *   mutate({
   *     url: '/api/users',
   *     method: 'POST',
   *     data: { name: 'John Doe', email: 'john@example.com' }
   *   });
   * };
   * ```
   *
   * @example
   * ```tsx
   * // Delete with optimistic updates
   * const { mutate } = useMutate<void, unknown, { previousData: User[] }>({
   *   onMutate: async ({ url }) => {
   *     const userId = url.split('/').pop();
   *     await queryClient.cancelQueries({ queryKey: ['users'] });
   *
   *     const previousData = queryClient.getQueryData<User[]>(['users']);
   *     queryClient.setQueryData<User[]>(['users'], (old) =>
   *       old?.filter(user => user.id !== userId) || []
   *     );
   *
   *     return { previousData };
   *   },
   *   onError: (err, variables, context) => {
   *     if (context?.previousData) {
   *       queryClient.setQueryData(['users'], context.previousData);
   *     }
   *   },
   *   onSettled: () => {
   *     queryClient.invalidateQueries({ queryKey: ['users'] });
   *   }
   * });
   * ```
   *
   * @example
   * ```tsx
   * // With custom config
   * const { mutateAsync } = useMutate();
   *
   * try {
   *   const result = await mutateAsync({
   *     url: '/api/upload',
   *     method: 'PUT',
   *     data: formData,
   *     config: {
   *       headers: { 'Content-Type': 'multipart/form-data' },
   *       timeout: 60000
   *     }
   *   });
   * } catch (error) {
   *   // Handle error
   * }
   * ```
   */
  const { getToken } = useAuth();
  const lastSuccessDataRef = useRef<TData | undefined>(undefined);

  const mutationFn = useCallback(
    async ({ url, method = 'POST', data, config }: MutationFnArgs) => {
      try {
        const token = await getToken();
        const response = await api.request<TData>({
          url,
          method,
          data,
          timeout: 30000,
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
            ...config?.headers,
          },
          ...config,
        });
        lastSuccessDataRef.current = response.data;
        return response.data;
      } catch (error) {
        if (error && typeof error === 'object' && 'isAxiosError' in error) {
          const axiosError = error as AxiosError;
          const status = axiosError.response?.status;
          if (status === 401 || status === 403) {
            throw new Error('Authentication failed. Please log in again.');
          }
          if (!axiosError.response) {
            throw new Error('Network error. Please check your connection.');
          }
        }
        throw error;
      }
    },
    [getToken]
  );

  const mutation = useMutation<TData, TError, MutationFnArgs, TContext>({
    mutationFn,
    ...options,
  });

  return useMemo(
    () => ({
      ...mutation,
      lastSuccessData: lastSuccessDataRef.current,
    }),
    [mutation]
  );
};
