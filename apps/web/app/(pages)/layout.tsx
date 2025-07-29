import type { PropsWithChildren } from 'react';
import Nav from '@/components/sections/nav';
import MainSection from '@/components/wrappers/main';

const layout = ({ children }: PropsWithChildren) => {
  return (
    <MainSection>
      <Nav />
      {children}
    </MainSection>
  );
};

export default layout;
