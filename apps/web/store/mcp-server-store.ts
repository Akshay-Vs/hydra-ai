import { create } from 'zustand';
import type { MCPServer } from '@/types/mcp-server';

type MCPServerStore = {
  mcp_servers: MCPServer[];
  setMCPServers: (mcp_servers: MCPServer[]) => void;
  deleteMCPServer: (id: string) => void;
};

export const useMCPServerStore = create<MCPServerStore>(set => ({
  mcp_servers: [],
  setMCPServers: (mcp_servers: MCPServer[]) => set({ mcp_servers }),
  deleteMCPServer: (id: string) =>
    set(state => ({
      mcp_servers: state.mcp_servers.filter(server => server.id !== id),
    })),
}));
