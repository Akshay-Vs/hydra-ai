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
      color: '#879CA7',
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
      color: '#879CA7',
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
      color: '#879CA7',
    },
  },
  {
    id: 'clx006',
    timestamp: '2025-07-29T10:29:34.12Z',
    source: {
      name: 'telemetry',
      color: '#E4B797',
    },
    message: {
      text: 'New ingestion pipeline registered: /pipelines/ingest-main-v2',
      color: '#879CA7',
    },
  },
  {
    id: 'clx007',
    timestamp: '2025-07-29T10:30:45.77Z',
    source: {
      name: 'diagnostics',
      color: '#97B8E4',
    },
    message: {
      text: 'Result: 14 errors, 2 warnings, 184 checks passed',
      color: '#879CA7',
    },
  },
  {
    id: 'clx008',
    timestamp: '2025-07-29T10:32:21.42Z',
    source: {
      name: 'autofix',
      color: '#97E4B5',
    },
    message: {
      text: 'Patched config.yaml with failover=true',
      color: '#879CA7',
    },
  },
  {
    id: 'clx009',
    timestamp: '2025-07-29T10:33:59.90Z',
    source: {
      name: 'agent-core',
      color: '#E4D297',
    },
    message: {
      text: 'New node registered: Node-07 (region=eu-west-2)',
      color: '#879CA7',
    },
  },
  {
    id: 'clx010',
    timestamp: '2025-07-29T10:35:10.22Z',
    source: {
      name: 'telemetry',
      color: '#E4B797',
    },
    message: {
      text: 'Exported logs to https://logs.example.com/export/789fdgheA',
      color: '#879CA7',
    },
  },
  {
    id: 'clx011',
    timestamp: '2025-07-29T10:36:42.88Z',
    source: {
      name: 'diagnostics',
      color: '#97B8E4',
    },
    message: {
      text: 'Disk usage warning: /var/log at 92%',
      color: '#879CA7',
    },
  },
  {
    id: 'clx012',
    timestamp: '2025-07-29T10:38:01.66Z',
    source: {
      name: 'autofix',
      color: '#97E4B5',
    },
    message: {
      text: 'Cleared old logs from /var/log/archive/',
      color: '#879CA7',
    },
  },
];
const LiveTail = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
  };

  return (
    <div className="full relative">
      <div className="flex justify-between items-center sticky top-0 z-10 pb-2 pt-4 bg-surface-3-dark">
        <h1 className="text-2xl">Live Trail</h1>
        <IconButton isActive={isCollapsed} onClick={toggleCollapse}>
          {isCollapsed ? (
            <UnfoldVertical size={20} className="text-accent-dark" />
          ) : (
            <FoldVertical size={20} />
          )}
        </IconButton>
      </div>

      <div className="table w-auto font-mono mt-4 overflow-auto">
        {logs.map(logGroup => (
          <div key={logGroup.id} className="table-row">
            <LogEntry text={logGroup.timestamp} color="#587584" className="whitespace-nowrap" />
            <LogEntry
              text={logGroup.source.name}
              color={logGroup.source.color}
              className="opacity-85"
            />
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
