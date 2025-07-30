'use client';
import { useState } from 'react';
import { Button } from '@hydra/ui/button';
import DatabaseUsageChart from '../tokens/database-usage-metrics';
import AgentWindow from './agent-window';

const UsageMetrics = () => {
  const tabs = [
    {
      key: 'database',
      label: 'Database',
      onClick: () => console.log('Database clicked'),
    },
    {
      key: 'agent',
      label: 'Agent',
      onClick: () => console.log('Agent clicked'),
    },
  ];

  const [activeTab, setActiveTab] = useState(tabs[0].key);

  const handleTabClick = (key: string) => {
    setActiveTab(key);
    const tab = tabs.find(tab => tab.key === key);
    if (tab) {
      tab.onClick();
    }
  };

  return (
    <div className="full">
      <div className="flex items-center gap-4">
        {tabs.map(tab => (
          <Button
            key={tab.key}
            onClick={() => handleTabClick(tab.key)}
            className={`h-12 px-8 rounded-3xl ${activeTab === tab.key && 'bg-active-dark text-accent-dark hover:bg-active-dark/90'}`}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <div className={`py-2 full ${activeTab === 'database' ? 'flex' : 'hidden'}`}>
        <DatabaseUsageChart />{' '}
      </div>

      <div className={`py-2 full ${activeTab === 'agent' ? 'flex' : 'hidden'}`}>
        <AgentWindow />
      </div>
    </div>
  );
};

export default UsageMetrics;
