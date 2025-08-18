import type { MouseEvent } from 'react';
import { cn } from '@hydra/ui/libs/utils';
import type { BaseProps } from '@/types/baseprops';

const Block = ({
  className,
  children,
  onClick,
}: BaseProps & { onClick?: (e: MouseEvent<HTMLDivElement>) => void }) => {
  return (
    <section
      onClick={onClick}
      className={cn(
        'w-1/2 h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark center relative',
        className
      )}
    >
      {children}
    </section>
  );
};

export default Block;
