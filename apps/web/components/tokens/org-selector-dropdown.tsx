'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
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

const OrgSelectorDropDown = () => {
  const { orgs, selectedOrg, setSelectedOrg, setOrgs } = useOrgStore();
  const { data, isLoading, error } = useFetch<Organization[]>(['orgs'], '/orgs');
  const router = useRouter();

  useEffect(() => {
    // Initialize with the first org or a default value
    if (!selectedOrg && orgs.length > 0) {
      setSelectedOrg(orgs[0].name);
    }
  }, [selectedOrg, orgs, setSelectedOrg, setOrgs]);

  useEffect(() => {
    if (data) {
      setOrgs(data);
    }
  }, [data, setOrgs]);

  const isSelected = (org: string) => {
    return selectedOrg === org;
  };

  if (orgs.length === 0 && !isLoading) {
    router.push('/onboarding');
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="bg-surface-2-dark h-full w-46 center gap-2 border-2 border-border-dark rounded-default p-1 px-6 active:outline-none focus-visible:outline-none focus:outline-2 focus:outline-offset-2 focus:outline-accent-dark"
        disabled={isLoading}
      >
        {orgs.length > 0 ? (
          <>
            <p className="w-46 center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
              {selectedOrg}
            </p>
            <ChevronDown className="h-6 w-6 text-dull-dark pt-1" />
          </>
        ) : (
          <p className="w-46 center overflow-x-hidden text-ellipsis line-clamp-1 select-none">
            No Orgs
          </p>
        )}
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-surface-2-dark border-2 text-text-dark border-border-dark rounded-default p-2 w-46">
        {orgs.map(org => (
          <DropdownMenuCheckboxItem
            key={org.id}
            checked={isSelected(org.name)}
            onCheckedChange={() => setSelectedOrg(org.name)}
            className={cn(isSelected(org.name) && 'text-accent-dark')}
          >
            {org.name}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default OrgSelectorDropDown;
