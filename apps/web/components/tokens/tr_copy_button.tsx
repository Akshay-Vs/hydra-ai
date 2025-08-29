'use client';
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

type Props = {
  value: string | null;
  label: string;
  placeholder?: string;
};

const CopyButton = ({ value, label, placeholder = '_' }: Props) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!value) return;

    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (!value) return <span className="text-gray-400">{placeholder}</span>;

  return (
    <div className="flex items-center gap-2 group">
      <span className="max-w-[340px] truncate" title={value}>
        {value}
      </span>
      <button
        onClick={handleCopy}
        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-active-dark hover:text-accent-dark text-dull-dark rounded"
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
