import { create } from 'zustand';
import type { Organization } from '@/types/org';

interface OrgStore {
  orgs: Organization[];
  selectedOrg: Organization | null;
  selectedOrgId: string | null;
  setOrgs: (orgs: Organization[]) => void;
  setSelectedOrg: (org: Organization) => void;
}

export const useOrgStore = create<OrgStore>(set => ({
  orgs: [],
  selectedOrg: null,
  selectedOrgId: null,
  setOrgs: orgs => set({ orgs }),
  setSelectedOrg: org => {
    set({ selectedOrg: org });
  },
}));
