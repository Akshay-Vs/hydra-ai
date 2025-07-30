import AgentInput from '../tokens/agent-input';
import AgentSelector from '../tokens/agent-selector';
import LogEntry from '../tokens/log-entry';

const logs = [
  {
    id: 'clx002',
    timestamp: '2025-07-29 10:23:47',
    source: {
      name: 'DataCollectionAgent',
      color: '#E497BC',
    },
    message: {
      text: 'Agent initialized for incident INC-20250127-145623-001',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx003',
    timestamp: '2025-07-29 10:23:48',
    source: {
      name: 'DataCollectionAgent',
      color: '#E497BC',
    },
    message: {
      text: 'Starting multi-source data gathering for service: payment-service',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx004',
    timestamp: '2025-07-29 10:23:52',
    source: {
      name: 'RootCauseAgent',
      color: '#B397E4',
    },
    message: {
      text: 'Received context from DataCollectionAgent',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx005',
    timestamp: '2025-07-29 10:23:57',
    source: {
      name: 'RootCauseAgent',
      color: '#B397E4',
    },
    message: {
      text: `┌─ 12:30:15 - Code deployment v2.4.1 (CATALYST)
├─ 12:53:42 - First memory usage anomaly detected
├─ 13:45:23 - GC frequency increased (5/min → 23/min)
├─ 14:12:15 - First OutOfMemoryError logged
└─ 14:56:23 - Current: Memory at 95% capacity (CRITICAL)`,
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx0043',
    timestamp: '2025-07-29 10:24:07',
    source: {
      name: 'DataCollectionAgent',
      color: '#E497BC',
    },
    message: {
      text: 'Recent deployment found: v2.4.1 deployed at 2025-01-27T12:30:15Z',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx0233',
    timestamp: '2025-07-29 10:23:42',
    source: {
      name: 'SolutionPlanningAgent',
      color: '#B2E497',
    },
    message: {
      text: 'Received RCA from RootCauseAgent',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx0562',
    timestamp: '2025-07-29 10:23:42',
    source: {
      name: 'SolutionPlanningAgent',
      color: '#B2E497',
    },
    message: {
      text: 'Received RCA from RootCauseAgent',
      color: '#DDDDDD',
    },
  },
  {
    id: 'clx502',
    timestamp: '2025-07-29 10:23:42',
    source: {
      name: 'SolutionPlanningAgent',
      color: '#B2E497',
    },
    message: {
      text: 'Received RCA from RootCauseAgent',
      color: '#DDDDDD',
    },
  },
];

const AgentWindow = () => {
  return (
    <div className="full relative col pb-4">
      <div className="w-full  h-full overflow-auto">
        {logs.map(logGroup => (
          <div key={logGroup.id} className="table-row">
            <LogEntry text={logGroup.timestamp} color="#587584" className="whitespace-nowrap" />
            <LogEntry text={logGroup.source.name} color={logGroup.source.color} />
            <LogEntry
              text={logGroup.message.text}
              color={logGroup.message.color}
              className="break-all whitespace-pre-wrap"
            />
          </div>
        ))}
      </div>
      <div className="w-full h-[10%] center flex gap-4 items-center">
        <AgentInput />
        <AgentSelector />
      </div>
    </div>
  );
};

export default AgentWindow;
