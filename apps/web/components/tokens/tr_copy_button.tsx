'use client';
import { cn } from '@hydra/ui/libs/utils';
import { Copy, Check } from 'lucide-react';
import useClipboard from '@/hooks/use-clipboard';

type Props = {
  value: string | null;
  label: string;
  placeholder?: string;
  always_visible?: boolean;
};

const CopyButton = ({ value, label, placeholder = '_', always_visible = false }: Props) => {
  const { handleCopy, copied } = useClipboard();
  if (!value) return <span className="text-gray-400">{placeholder}</span>;

  return (
    <div className="flex items-center gap-2 group">
      <span className="max-w-[340px] truncate" title={value}>
        {value}
      </span>
      <button
        onClick={() => handleCopy(value)}
        className={cn(
          'p-1 hover:bg-active-dark hover:text-accent-dark text-dull-dark rounded',
          !always_visible && 'opacity-0 group-hover:opacity-100 transition-opacity'
        )}
        title={`Copy ${label}`}
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-600" />
        ) : (
          <Copy className="h-4 w-4 text-inherit" />
        )}
      </button>
    </div>
  );
};

export default CopyButton;
