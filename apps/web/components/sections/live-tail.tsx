'use client';
import { useEffect, useRef, useState } from 'react';
import { cn } from '@hydra/ui/libs/utils';
import { ArrowDown, FoldVertical, UnfoldVertical } from 'lucide-react';
import { useSocket } from '@/hooks/use-socket';
import type { LogEntry as LogEntryType } from '@/types/log-entry';
import IconButton from '../tokens/icon-button';
import LogEntry from '../tokens/log-entry';
import Spinner from '../tokens/spinner';

const LiveTail = () => {
  const ref = useRef<HTMLDivElement>(null);

  const [isCollapsed, setIsCollapsed] = useState(false);
  const { isConnected, error, on, off } = useSocket();
  const [logs, setLogs] = useState<LogEntryType[]>([]);
  const [isHovered, setIsHovered] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  const scrollToBottom = () => {
    if (ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const handleNewLog = (log: LogEntryType) => {
      setLogs(prevLogs => [...prevLogs, log].slice(-100));
      if (ref.current && !isHovered && isAtBottom) {
        scrollToBottom();
      }

      if (ref?.current?.parentElement) {
        const { scrollTop, scrollHeight, clientHeight } = ref.current.parentElement;
        const margin = 200;
        const atBottom = scrollTop + clientHeight >= scrollHeight - margin;
        setIsAtBottom(atBottom);
        if (atBottom && !isHovered) {
          ref.current.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };
    on<LogEntryType>('new-log', handleNewLog);

    return () => {
      off<LogEntryType>('new-log', handleNewLog);
    };
  }, [on, off, isHovered, isAtBottom]);

  return (
    <div className="full">
      <div className="flex justify-between items-center z-10 pb-2 pt-4 bg-surface-3-dark relative">
        <h1 className="text-2xl">Live Trail</h1>
        <IconButton
          isActive={isCollapsed}
          onClick={toggleCollapse}
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          {isCollapsed ? (
            <UnfoldVertical size={20} className="text-accent-dark" />
          ) : (
            <FoldVertical size={20} />
          )}
        </IconButton>
      </div>

      <div
        className="w-full font-mono mt-4 overflow-y-auto overflow-x-hidden max-h-96"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {logs.length > 0 &&
          logs.map(logGroup => (
            <div key={logGroup.id} className="flex min-w-0">
              {' '}
              {/* min-w-0 is key */}
              <LogEntry
                text={logGroup.timestamp}
                color="#587584"
                className="whitespace-nowrap flex-shrink-0"
              />
              <LogEntry
                text={logGroup.source.name}
                color={logGroup.source.color}
                className="opacity-85 flex-shrink-0"
              />
              <LogEntry
                text={logGroup.message.text}
                color={logGroup.message.color}
                className={cn(
                  'flex-1 min-w-0',
                  isCollapsed
                    ? 'truncate overflow-hidden whitespace-nowrap'
                    : 'break-all whitespace-pre-wrap overflow-hidden'
                )}
              />
            </div>
          ))}
        {isConnected && !logs.length ? (
          <div className="abs-center">
            <p className="text-base text-center text-dull-dark">No logs yet.</p>
          </div>
        ) : null}

        {!isConnected && !error && (
          <div className="abs-center gap-3 col-center">
            <Spinner />
            <p className="text-sm text-dull-dark/70">Connecting to live logs...</p>
          </div>
        )}

        {error && (
          <div className="abs-center">
            <p className="text-base text-center text-red-500">Error: {error}</p>
          </div>
        )}

        <div ref={ref} />
      </div>
      {!isAtBottom && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
          <IconButton isActive onClick={scrollToBottom}>
            <ArrowDown size={20} />
          </IconButton>
        </div>
      )}
    </div>
  );
};

export default LiveTail;
