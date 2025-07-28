import Image from 'next/image';
import Link from 'next/link';
import { Bell, HomeIcon, Link as Link2, Waypoints } from 'lucide-react';

import Logo from '@/public/images/Hydra_Logo.svg';
import IconButton from '../tokens/icon-button';

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
      <div className="flex center gap-12 h-14">
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
              <IconButton isActive={button.isActive}>{button.icon}</IconButton>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Nav;
