import { cn } from '@hydra/ui/libs/utils';

type Props = {
  text: string;
  color: string;
  className?: string;
};

const LogEntry = ({ text, color, className }: Props) => {
  return (
    <div
      className={cn('table-cell pr-6 pb-4 font-medium font-mono shrink-0', className)}
      style={{ color }}
    >
      {text}
    </div>
  );
};

export default LogEntry;
