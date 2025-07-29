'use client';
import { useState } from 'react';
import { cn } from '@hydra/ui/libs/utils';
import { FoldVertical, UnfoldVertical } from 'lucide-react';
import type { LogEntry as LogEntryType } from '@/types/log-entry';
import IconButton from '../tokens/icon-button';
import LogEntry from '../tokens/log-entry';

const logs: LogEntryType[] = [
  {
    id: 'clx001',
    timestamp: '2025-07-29T10:22:11.04Z',
    source: {
      name: 'agent-core',
      color: '#E4D297',
    },
    message: {
      text: 'Heartbeat signal received from Node-03',
      color: '#B3CCD9',
    },
  },
  {
    id: 'clx002',
    timestamp: '2025-07-29T10:23:47.10Z',
    source: {
      name: 'telemetry',
      color: '#E4B797',
    },
    message: {
      text: 'Anomaly detected in query latency (avg > 2.1s)',
      color: '#B3CCD9',
    },
  },
  {
    id: 'clx003',
    timestamp: '2025-07-29T10:25:13.88Z',
    source: {
      name: 'diagnostics',
      color: '#97B8E4',
    },
    message: {
      text: 'curl -sS https://telemetry.betterstack.com/flights/XBQ876a9NytwRXhjgGZoD7uD | bash',
      color: '#9F97E4',
    },
  },
  {
    id: 'clx004',
    timestamp: '2025-07-29T10:26:32.59Z',
    source: {
      name: 'autofix',
      color: '#97E4B5',
    },
    message: {
      text: 'Restarted affected replica. Monitoring recovery.',
      color: '#E497A6',
    },
  },
  {
    id: 'clx005',
    timestamp: '2025-07-29T10:28:02.00Z',
    source: {
      name: 'agent-core',
      color: '#E4D297',
    },
    message: {
      text: 'Recovery complete. All systems nominal.',
      color: '#B3CCD9',
    },
  },
];

const LiveTail = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  return (
    <div className="full py-1">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl">Live Trail</h2>
        <IconButton isActive={isCollapsed} onClick={toggleCollapse}>
          {isCollapsed ? (
            <UnfoldVertical size={20} className="text-accent-dark" />
          ) : (
            <FoldVertical size={20} />
          )}
        </IconButton>
      </div>

      <div className="table w-auto font-mono mt-4">
        {logs.map(logGroup => (
          <div key={logGroup.id} className="table-row">
            <LogEntry text={logGroup.timestamp} color="#587584" className="whitespace-nowrap" />
            <LogEntry text={logGroup.source.name} color={logGroup.source.color} />
            <LogEntry
              text={logGroup.message.text}
              color={logGroup.message.color}
              className={cn(
                isCollapsed
                  ? 'truncate max-w-[32rem] whitespace-nowrap overflow-hidden'
                  : 'break-all whitespace-pre-wrap'
              )}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveTail;
