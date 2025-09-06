import { create } from 'zustand';
import type { MCPServer } from '@/types/mcp-server';

type MCPServerStore = {
  mcp_servers: MCPServer[];
  setMCPServers: (mcp_servers: MCPServer[]) => void;
};

export const useMCPServerStore = create<MCPServerStore>(set => ({
  mcp_servers: [],
  setMCPServers: (mcp_servers: MCPServer[]) => set({ mcp_servers }),
}));
