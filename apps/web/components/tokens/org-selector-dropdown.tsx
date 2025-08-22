'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from '@hydra/ui/dropdown-menu';
import { cn } from '@hydra/ui/libs/utils';
import { ChevronDown } from 'lucide-react';
import { useFetch } from '@/hooks/use-fetch';
import { useOrgStore } from '@/store/org-store';
import type { Organization } from '@/types/org';
import AddOrgButton from './add-org-button';

const OrgSelectorDropDown = () => {
  const { orgs, selectedOrg, setSelectedOrg, setOrgs } = useOrgStore();
  const { data, isLoading, error, refetch } = useFetch<Organization[]>(['orgs'], '/org');
  const params = useParams<{ orgid: string }>();
  const router = useRouter();

  useEffect(() => {
    if (data) {
      setOrgs(data);

      if (params.orgid) {
        const org = data.find(org => org.id === params.orgid)?.name;
        if (!org?.length) return router.push('/404');
        setSelectedOrg(org);
      }
    }
  }, [data, setOrgs, params, setSelectedOrg]);

  const isSelected = (org: string) => {
    return selectedOrg === org;
  };

  const selectOrg = (org: string) => {
    const selectedOrganization = orgs.find(o => o.name === org);
    if (selectedOrganization) {
      setSelectedOrg(selectedOrganization.name);
      router.push(`/org/${selectedOrganization.id}`);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="bg-surface-2-dark h-full w-46 center gap-2 border-2 border-border-dark rounded-default p-1 px-6 active:outline-none focus-visible:outline-none focus:outline-2 focus:outline-offset-2 focus:outline-accent-dark"
        disabled={isLoading}
        onClick={() => refetch()}
      >
        {orgs.length > 0 && !isLoading ? (
          <>
            <p className="w-46 center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
              {selectedOrg}
            </p>
            <ChevronDown className="h-6 w-6 text-dull-dark pt-1" />
          </>
        ) : null}

        {orgs.length === 0 && !isLoading && !error ? (
          <p className="w-46 center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
            No Orgs
          </p>
        ) : null}

        {isLoading && (
          <p className="w-46 center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
            Loading...
          </p>
        )}
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-surface-2-dark border-2 text-text-dark border-border-dark col gap-3 rounded-default p-2 w-46">
        {orgs.map(org => (
          <DropdownMenuCheckboxItem
            key={org.id}
            checked={isSelected(org.name)}
            onCheckedChange={() => selectOrg(org.name)}
            className={(cn(isSelected(org.name) && 'text-accent-dark'), 'text-lg')}
          >
            {org.name}
          </DropdownMenuCheckboxItem>
        ))}
        <AddOrgButton />
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default OrgSelectorDropDown;
