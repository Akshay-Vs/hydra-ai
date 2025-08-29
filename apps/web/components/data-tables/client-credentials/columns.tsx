'use client';
import type { ColumnDef } from '@tanstack/react-table';
import RevokeTokenButton from '@/components/tokens/revoke-token-button';
import CopyButton from '@/components/tokens/tr_copy_button';

export type Credential = {
  id: string;
  organization_id: string;
  client_secret: string | null;
  last_used: string | null;
  expires_at: string;
  created_at: string;
  is_active: boolean;
};

export const columns: ColumnDef<Credential>[] = [
  {
    accessorKey: 'organization_id',
    header: 'Organization ID',
    cell: ({ row }) => (
      <CopyButton value={row.getValue('organization_id')} label="Organization ID" />
    ),
  },
  {
    accessorKey: 'id',
    header: 'Credential ID',
    cell: ({ row }) => <CopyButton value={row.getValue('id')} label="Credential ID" />,
  },
  {
    accessorKey: 'client_secret',
    header: 'Client Secret',
    cell: ({ row }) => (
      <CopyButton
        value={row.getValue('client_secret')}
        label="Client Secret"
        placeholder="**************************"
      />
    ),
  },
  {
    accessorKey: 'expires_at',
    header: 'Expires At',
    cell: ({ row }) => new Date(row.getValue('expires_at')).toLocaleString(),
  },
  {
    accessorKey: 'actions',
    header: 'Actions',
    cell: ({ row }) => (
      <RevokeTokenButton
        orgId={row.getValue('organization_id')}
        credentialId={row.getValue('id')}
      />
    ),
  },
];
