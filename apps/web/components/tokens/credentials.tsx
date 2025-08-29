'use client';
import { Button } from '@hydra/ui/button';
import { useFetch } from '@/hooks/use-fetch';
import { useOrgStore } from '@/store/org-store';
import { columns, type Credential } from '../data-tables/client-credentials/columns';
import DataTable from '../data-tables/data-table';
import Block from '../wrappers/block';
import Spinner from './spinner';

const Credentials = () => {
  const { selectedOrg } = useOrgStore();
  const { data, isLoading } = useFetch<Credential[]>(
    ['client_credentials'],
    `/org/credentials/${selectedOrg?.id}`
  );

  return (
    <Block className="full col min-h-[48dvh] !justify-start items-start">
      <div className="flex w-full justify-between items-center pb-4">
        <h1 className="px-1 text-2xl">Client Connection Credentials</h1>
        <Button className="px-8 h-14 border-2 border-border-dark bg-surface-2-dark">
          New Credential
        </Button>
      </div>
      <div className="full center">
        {isLoading ? (
          <div className="col center full min-h-[48dvh]">
            <Spinner />
            <p className="text-center text-muted-foreground pt-2">Loading credentials...</p>
          </div>
        ) : null}

        {!isLoading && !data && (
          <div className="col center full min-h-[48dvh]">
            <p className="text-center text-muted-foreground">No credentials found.</p>
          </div>
        )}

        {data ? <DataTable columns={columns} data={data} /> : null}
      </div>
    </Block>
  );
};

export default Credentials;
