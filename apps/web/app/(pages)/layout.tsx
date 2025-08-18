import type { PropsWithChildren } from 'react';
import Nav from '@/components/sections/nav';
import ModalProvider from '@/components/tokens/modal-provider';
import MainSection from '@/components/wrappers/main';

const layout = ({ children }: PropsWithChildren) => {
  return (
    <>
      <ModalProvider />
      <MainSection>
        <Nav />
        {children}
      </MainSection>
    </>
  );
};

export default layout;
