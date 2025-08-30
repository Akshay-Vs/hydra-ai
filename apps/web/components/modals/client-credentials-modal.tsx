import { Check, Copy, Info } from 'lucide-react';
import useClipboard from '@/hooks/use-clipboard';
import Block from '../wrappers/block';

type Props = {
  credentials: Record<string, string>;
};

const ClientCredentialsModal = ({ credentials }: Props) => {
  const { copied, handleCopy } = useClipboard();

  const copy = () => {
    const value = Object.entries(credentials)
      .map(([key, value]) => `${key.toUpperCase()}=${value}`)
      .join('\n');
    handleCopy(value);
  };

  return (
    <div className="col gap-4">
      <Block className="w-full h-fit  mt-6 cursor-text !justify-start items-start p-6 relative bg-black/10 overflow-clip text-clip">
        <button
          onClick={copy}
          className="p-1 hover:bg-active-dark hover:text-accent-dark text-dull-dark rounded absolute top-6 right-6"
          title="Copy credentials"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-600" />
          ) : (
            <Copy className="h-4 w-4 text-inherit" />
          )}
        </button>

        <div className="col font-mono ">
          {Object.entries(credentials).map(([key, value]) => (
            <div key={key} className="flex gap-1 mb-2">
              <span className="text-muted-foreground gap-1 flex">
                {key.toUpperCase()}
                <span>=</span>
              </span>
              <span className="flex-wrap overflow-clip">{value}</span>
            </div>
          ))}
        </div>
      </Block>

      <p className="text-sm text-dull-dark px-4">
        <Info className="inline mb-1 mr-2 h-4 w-4" />
        The client secret is shown only once, copy and store it securely. .
      </p>
    </div>
  );
};

export default ClientCredentialsModal;
