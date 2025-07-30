import type { PropsWithChildren } from 'react';

const MainSection = ({ children }: PropsWithChildren) => {
  return <main className="min-h-screen w-screen p-4 font-sans">{children}</main>;
};

export default MainSection;
