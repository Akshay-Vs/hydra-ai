import { useMCPServerStore } from '@/store/mcp-server-store';
import Block from '../wrappers/block';

const MCPServerList = () => {
  const { mcp_servers } = useMCPServerStore();
  return (
    <div className="flex flex-wrap gap-6 full px-4">
      {mcp_servers.map(server => (
        <Block className="h-40 w-40" key={server.id}>
          {server.name}
        </Block>
      ))}
    </div>
  );
};

export default MCPServerList;
