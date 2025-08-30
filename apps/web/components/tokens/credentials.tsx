'use client';
import { useFetch } from '@/hooks/use-fetch';
import { useOrgStore } from '@/store/org-store';
import { columns, type Credential } from '../data-tables/client-credentials/columns';
import DataTable from '../data-tables/data-table';
import Block from '../wrappers/block';
import NewCredentialButton from './new-credentials-button';
import Spinner from './spinner';

const Credentials = () => {
  const { selectedOrg } = useOrgStore();
  const { data, isLoading } = useFetch<Credential[]>(
    ['client_credentials'],
    `/org/credentials/${selectedOrg?.id}`
  );

  return (
    <Block className="full col min-h-[48dvh] !justify-start items-start relative">
      <div className="flex w-full justify-between items-center pb-4">
        <h1 className="px-2 text-2xl">Client Connection Credentials</h1>
        <NewCredentialButton />
      </div>
      <div className="full center">
        {isLoading ? (
          <div className="col center full abs-center">
            <Spinner />
            <p className="text-center text-muted-foreground pt-2">Loading credentials...</p>
          </div>
        ) : null}

        {!isLoading && !data && (
          <div className="col center full abs-center">
            <p className="text-center text-muted-foreground">No credentials found.</p>
          </div>
        )}

        {data ? <DataTable columns={columns} data={data} /> : null}
      </div>
    </Block>
  );
};

export default Credentials;
