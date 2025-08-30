import type { ComponentProps, PropsWithChildren } from 'react';
import { Button } from '@hydra/ui/button';
import { cn } from '@hydra/ui/libs/utils';

type iconButtonProps = PropsWithChildren &
  ComponentProps<'button'> & {
    onClick?: () => void;
    isActive?: boolean;
    asChild?: boolean;
    tabindex?: number;
  };

const IconButton = ({
  children,
  onClick,
  isActive,
  asChild,
  tabindex,
  title,
  'aria-label': label,
}: iconButtonProps) => {
  return (
    <Button
      variant="icon"
      className={cn('text-3xl  hover:bg-accent-dark/20', isActive && 'bg-active-dark ')}
      size="icon"
      onClick={onClick}
      data-active={isActive}
      asChild={asChild}
      tabIndex={tabindex}
      title={title}
      aria-label={label}
    >
      {children}
    </Button>
  );
};

export default IconButton;
