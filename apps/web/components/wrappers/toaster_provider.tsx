'use client';

import { Toaster } from '@hydra/ui/sonner';
import useIsClient from '@/hooks/use-isclient';

const ToasterProvider = () => {
  const mounted = useIsClient();

  if (!mounted) {
    return null;
  }

  return <Toaster />;
};

export default ToasterProvider;
