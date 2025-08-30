'use client';
import Link from 'next/link';
import { useClerk } from '@clerk/nextjs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from '@hydra/ui/dropdown-menu';
import { ArrowUpRight, User2 } from 'lucide-react';

const UserProfileDropDown = () => {
  const { user, signOut } = useClerk();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="hover:bg-accent-dark/20 !h-10 !w-10 center rounded-xl">
        <User2 className="!h-6 !w-6" />
      </DropdownMenuTrigger>

      <DropdownMenuContent className="bg-surface-2-dark border-2 text-text-dark border-border-dark col gap-3 rounded-default mt-2 mr-4 p-2 w-[20rem]">
        <DropdownMenuLabel className="text-base text-dull-dark/60">Logged in as</DropdownMenuLabel>
        <DropdownMenuGroup className="gap-2">
          <DropdownMenuItem>{user?.fullName}</DropdownMenuItem>
          <DropdownMenuItem>{user?.emailAddresses[0]?.toString()}</DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />

        <DropdownMenuItem>
          <Link href="https://github.com/akshay-vs/hydra-ai" target="_blank">
            GitHub
          </Link>
          <DropdownMenuShortcut>
            <ArrowUpRight className="!h-4 !w-4" />
          </DropdownMenuShortcut>
        </DropdownMenuItem>
        <DropdownMenuItem>
          DevPost
          <DropdownMenuShortcut>
            <ArrowUpRight className="!h-4 !w-4" />
          </DropdownMenuShortcut>
        </DropdownMenuItem>
        <DropdownMenuSeparator />

        <DropdownMenuItem onClick={() => signOut()}>
          Log out
          <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserProfileDropDown;
