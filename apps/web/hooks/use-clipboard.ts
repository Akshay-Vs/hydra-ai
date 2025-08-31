import { useState } from 'react';

const useClipboard = () => {
  const [copied, setCopied] = useState(false);
  const handleCopy = async (value: string) => {
    if (!value) return;

    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return { copied, handleCopy };
};

export default useClipboard;
