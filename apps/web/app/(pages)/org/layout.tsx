import type { PropsWithChildren } from 'react';
import SplashScreenProvider from '@/components/wrappers/splash-screen-provider';

const layout = ({ children }: PropsWithChildren) => {
  return <SplashScreenProvider>{children}</SplashScreenProvider>;
};

export default layout;
