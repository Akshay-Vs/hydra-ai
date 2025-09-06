'use client';
import { useEffect } from 'react';
import { useFetch } from '@/hooks/use-fetch';
import { useMCPServerStore } from '@/store/mcp-server-store';
import { useOrgStore } from '@/store/org-store';
import type { MCPServer } from '@/types/mcp-server';
import Block from '../wrappers/block';
import AddThirdPartyButton from './add-third-party-button';
import MCPServerList from './mcp-servers-list';
import Spinner from './spinner';

const ThirdPartyIntegration = () => {
  const { selectedOrg } = useOrgStore();
  const { setMCPServers } = useMCPServerStore();
  const { data, isLoading } = useFetch<MCPServer[]>(['mcp_servers'], `/mcp/${selectedOrg?.id}`);

  useEffect(() => {
    if (data) {
      setMCPServers(data);
    }
  }, [data, setMCPServers]);

  return (
    <Block className="full col min-h-[28rem] !justify-start items-start relative">
      <div className="flex w-full justify-between pb-4">
        <h1 className="px-2 text-xl text-dull-dark font-medium p-2">Third Party Integrations</h1>
        <AddThirdPartyButton />
      </div>

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

        {data ? <MCPServerList /> : null}
      </div>
    </Block>
  );
};

export default ThirdPartyIntegration;
