'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { Organization } from '@clerk/nextjs/server';
import SplashScreen from '@/components/tokens/splash-screen';
import { useFetch } from '@/hooks/use-fetch';

export default function Home() {
  const { data, isLoading } = useFetch<Organization[]>(['orgs'], '/org');
  const router = useRouter();

  useEffect(() => {
    if (data && !isLoading) {
      if (data.length > 0) {
        // Redirect to the first organization's page
        router.push(`/org/${data[0].id}`);
      } else {
        router.push('/org/new');
      }
    }
  }, [data, router, isLoading]);

  if (!isLoading) {
    return null;
  }

  return <SplashScreen />;
}
