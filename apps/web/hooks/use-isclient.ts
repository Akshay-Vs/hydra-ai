import { useEffect, useState } from 'react';

/**
 * Hook to check if the component has mounted on the client side.
 * Returns `true` after the first render on the client.
 */
const useIsClient = (): boolean => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return isClient;
};

export default useIsClient;
