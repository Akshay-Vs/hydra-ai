import { useEffect, useState } from 'react';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@hydra/ui/dropdown-menu';
import { cn } from '@hydra/ui/libs/utils';
import { ChevronDown } from 'lucide-react';

const agents = [
  {
    id: 'ag001',
    label: 'DataCollectionAgent',
  },
  {
    id: 'ag002',
    label: 'RootCauseAgent',
  },
  {
    id: 'ag003',
    label: 'SolutionPlanningAgent',
  },
];

const AgentSelector = () => {
  const [selectedAgent, setSelectedAgent] = useState<string>();

  useEffect(() => {
    // Initialize with the first org or a default value
    if (!selectedAgent && agents.length > 0) {
      setSelectedAgent(agents[0].label);
    }
  }, [selectedAgent, setSelectedAgent]);

  const isSelected = (org: string) => {
    return selectedAgent === org;
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="bg-active-dark h-full w-fit center gap-2 border-2 border-border-dark p-1 px-6 active:outline-none focus-visible:outline-none focus:outline-2 focus:outline-offset-2 focus:outline-accent-dark rounded-lg border-none">
        <p className="w-fit center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
          {selectedAgent}
        </p>
        <ChevronDown className="h-6 w-6 text-dull-dark pt-1" />
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        className="bg-surface-2-dark border-2 text-text-dark border-border-dark rounded-default p-2 w-fit"
      >
        {agents.map(agent => (
          <DropdownMenuCheckboxItem
            key={agent.id}
            checked={isSelected(agent.label)}
            onCheckedChange={() => setSelectedAgent(agent.label)}
            className={cn(isSelected(agent.label) && 'text-accent-dark')}
          >
            {agent.label}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default AgentSelector;
