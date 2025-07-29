import type { PropsWithChildren } from 'react';
import { Button } from '@hydra/ui/button';
import { cn } from '@hydra/ui/libs/utils';

type iconButtonProps = PropsWithChildren & {
  onClick?: () => void;
  isActive?: boolean;
  asChild?: boolean;
  tabindex?: number;
};

const IconButton = ({ children, onClick, isActive, asChild, tabindex }: iconButtonProps) => {
  return (
    <Button
      variant="icon"
      className={cn('text-3xl  hover:bg-accent-dark/20', isActive && 'bg-active-dark ')}
      size="icon"
      onClick={onClick}
      data-active={isActive}
      asChild={asChild}
      tabIndex={tabindex}
    >
      {children}
    </Button>
  );
};

export default IconButton;
