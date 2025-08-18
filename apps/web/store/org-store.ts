import { create } from 'zustand';
import type { Organization } from '@/types/org';

interface OrgStore {
  orgs: Organization[];
  selectedOrg: string | null;
  setOrgs: (orgs: Organization[]) => void;
  setSelectedOrg: (org: string) => void;
}

export const useOrgStore = create<OrgStore>(set => ({
  orgs: [],
  selectedOrg: null,
  setOrgs: orgs => set({ orgs }),
  setSelectedOrg: org => set({ selectedOrg: org }),
}));
