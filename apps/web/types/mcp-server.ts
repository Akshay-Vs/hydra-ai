export type MCPServer = {
  id: string;
  name: string;
  description: string;
  url: string;
  icon: string;
  is_active: boolean;
  organization_id: string;
  created_at: Date;
  updated_at: Date | null;
};
