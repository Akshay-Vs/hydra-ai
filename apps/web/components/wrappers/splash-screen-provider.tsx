'use client';

import type { PropsWithChildren } from 'react';
import { useOrgStore } from '@/store/org-store';
import SplashScreen from '../tokens/splash-screen';

const SplashScreenProvider = ({ children }: PropsWithChildren) => {
  const { selectedOrg } = useOrgStore();
  return (
    <div>
      {!selectedOrg && <SplashScreen />}
      {children}
    </div>
  );
};

export default SplashScreenProvider;
