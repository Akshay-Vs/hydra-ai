import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@hydra/ui/button';
import { Bell, HomeIcon, Link as Link2, Settings, User2, Waypoints } from 'lucide-react';

import Logo from '@/public/images/Hydra_Logo.svg';
import IconButton from '../tokens/icon-button';
import OrgSelectorDropDown from '../tokens/org-selector-dropdown';

const Nav = () => {
  const navButtons = [
    {
      id: 'Home',
      icon: <HomeIcon className="h-6 w-6" />,
      href: '/',
      isActive: true,
    },
    {
      id: 'Nodes',
      icon: <Waypoints className="h-6 w-6" />,
      href: '/nodes',
      isActive: false,
    },
    {
      id: 'Integrations',
      icon: <Link2 className="h-6 w-6" />,
      href: '/integrations',
      isActive: false,
    },
    {
      id: 'Alerts',
      icon: <Bell className="h-6 w-6" />,
      href: '/alerts',
      isActive: false,
    },
  ];
  return (
    <nav className="w-full h-14 flex items-center justify-between">
      <div className="flex center gap-8 h-14">
        <Image
          src={Logo}
          height={48}
          width={48}
          alt="Hydra"
          className="full object-center object-contain"
        />

        <div className="bg-surface-2-dark h-full w-fit center gap-2 border-2 border-border-dark rounded-default p-1">
          {navButtons.map(button => (
            <Link key={button.id} href={button.href}>
              <IconButton isActive={button.isActive} tabindex={-1}>
                {button.icon}
              </IconButton>
            </Link>
          ))}
        </div>

        <OrgSelectorDropDown />
      </div>

      <div className="flex center gap-6 h-full">
        <div className="h-3 w-3 bg-green-300 rounded-full" />

        <div className="bg-surface-2-dark h-full w-fit center gap-3 border-2 border-border-dark rounded-default p-1">
          <Button variant="secondary" className="h-full" size="default">
            Invite Members
          </Button>

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
