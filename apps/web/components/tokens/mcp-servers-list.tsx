import { useEffect } from 'react';
import { Button } from '@hydra/ui/button';
import { Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useFetch } from '@/hooks/use-fetch';
import { useMutate } from '@/hooks/use-mutate';
import { useMCPServerStore } from '@/store/mcp-server-store';
import { useOrgStore } from '@/store/org-store';
import type { MCPServer } from '@/types/mcp-server';
import Block from '../wrappers/block';
import Spinner from './spinner';

const MCPServerList = () => {
  const { mcp_servers, setMCPServers, deleteMCPServer } = useMCPServerStore();
  const { selectedOrg } = useOrgStore();
  const { data, isLoading } = useFetch<MCPServer[]>(['mcp_servers'], `/mcp/${selectedOrg?.id}`);
  const { mutateAsync, isPending } = useMutate<MCPServer>({
    onError: error => {
      console.error('Error creating MCP configuration:', error);
    },
  });

  useEffect(() => {
    if (data) {
      setMCPServers(data);
    }
  }, [data, setMCPServers]);

  const handleDelete = async (id: string) => {
    try {
      await mutateAsync({
        url: `/mcp/${selectedOrg?.id}/${id}`,
        method: 'DELETE',
      });
      deleteMCPServer(id);
      toast.success('MCP server deleted');
    } catch {
      toast.error('Failed to delete MCP server');
    }
  };
  return (
    <div className="full">
      {isLoading ? (
        <div className="col center full abs-center">
          <Spinner />
          <p className="text-center text-muted-foreground pt-2">Loading mcp servers...</p>
        </div>
      ) : null}

      {!isLoading && !data && (
        <div className="col center full abs-center">
          <p className="text-center text-muted-foreground">No mcp servers found.</p>
        </div>
      )}

      {data ? (
        <div className="flex flex-wrap gap-6 full px-4">
          {mcp_servers.map(server => (
            <Block className="h-40 w-40 group relative" key={server.id}>
              {server.name}

              <div>
                <Button
                  className="absolute top-2 right-2 group-hover:block hidden bg-transparent"
                  onClick={() => handleDelete(server.id)}
                  disabled={isPending}
                >
                  {isPending ? <Spinner /> : <Trash2 size={16} className="text-red-400" />}
                </Button>
              </div>
            </Block>
          ))}
        </div>
      ) : null}
    </div>
  );
};

export default MCPServerList;
