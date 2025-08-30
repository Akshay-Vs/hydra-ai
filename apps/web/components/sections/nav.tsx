'use client';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@hydra/ui/libs/utils';
import { Bell, HomeIcon, Link as Link2, Settings, User2 } from 'lucide-react';

import Logo from '@/public/images/Hydra_Logo.svg';
import { useOrgStore } from '@/store/org-store';
import IconButton from '../tokens/icon-button';
import InviteMemberButton from '../tokens/invite-member-button';
import OrgSelectorDropDown from '../tokens/org-selector-dropdown';
import Spinner from '../tokens/spinner';

const Nav = () => {
  const pathname = usePathname();
  const { selectedOrg } = useOrgStore();

  const orgId = selectedOrg?.id;
  const base = `/org/${orgId}`;

  const navButtons = [
    {
      id: 'Home',
      icon: <HomeIcon className="h-6 w-6" />,
      href: base,
    },
    // {
    //   id: 'Nodes',
    //   icon: <Waypoints className="h-6 w-6" />,
    //   href: '/nodes',
    //   isActive: false,
    // },
    {
      id: 'Connect',
      icon: <Link2 className="h-6 w-6" />,
      href: `${base}/connect`,
    },
    {
      id: 'Notifications',
      icon: <Bell className="h-6 w-6" />,
      href: `${base}/notifications`,
    },
  ];

  const isActive = (href: string) => {
    return pathname === href;
  };

  return (
    <nav
      className={cn(
        pathname === '/' && 'opacity-0',
        'w-full h-14 flex items-center justify-between select-none'
      )}
    >
      <div className="flex center gap-8 h-14">
        <Image
          src={Logo}
          height={48}
          width={48}
          alt="Hydra"
          className="full object-center object-contain"
        />

        <div className="bg-surface-2-dark h-full w-fit center gap-2 border-2 border-border-dark rounded-default p-1">
          {orgId ? (
            navButtons.map(button => (
              <Link key={button.id} href={button.href}>
                <IconButton isActive={isActive(button.href)} tabindex={-1}>
                  {button.icon}
                </IconButton>
              </Link>
            ))
          ) : (
            <div className="w-32 center">
              <Spinner />
            </div>
          )}
        </div>
        <OrgSelectorDropDown />
      </div>

      <div className="flex center gap-6 h-full">
        <div className="h-3 w-3 bg-green-300 rounded-full" />

        <div className="bg-surface-2-dark h-full w-fit center gap-3 border-2 border-border-dark rounded-default p-1">
          <InviteMemberButton />
          <div>
            <IconButton isActive={false}>
              <Settings className="h-6 w-6" />
            </IconButton>

            <IconButton isActive={false}>
              <User2 className="h-6 w-6" />
            </IconButton>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Nav;
