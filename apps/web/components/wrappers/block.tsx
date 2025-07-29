import { cn } from '@hydra/ui/libs/utils';
import type { BaseProps } from '@/styles/types/baseprops';

const Block = ({ className, children }: BaseProps) => {
  return (
    <section
      className={cn(
        'w-1/2 h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark center',
        className
      )}
    >
      {children}
    </section>
  );
};

export default Block;
