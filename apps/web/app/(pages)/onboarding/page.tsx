'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SplashScreen from '@/components/tokens/splash-screen';
import { useBearerToken } from '@/hooks/use-bearer-token';
import useIsClient from '@/hooks/use-isclient';
import { useMutate } from '@/hooks/use-mutate';

type OnboardingData = {
  id: string;
  clerk_id: string;
  organization_id: string;
  created_at: string;
};

const OnboardingPage = () => {
  const router = useRouter();
  const isMounted = useIsClient();
  const { isLoaded } = useBearerToken();

  const { mutateAsync, error, isPending } = useMutate<OnboardingData>({
    onSuccess: data => {
      if (data && 'organization_id' in data) {
        router.push(`/org/${data.organization_id}`);
      }
    },
  });

  useEffect(() => {
    if (isLoaded) mutateAsync({ url: '/onboarding', method: 'POST' });
  }, [mutateAsync, isLoaded]);

  if (!isMounted) return null;
  if (error)
    return (
      <SplashScreen
        label="An error occurred during onboarding. Please try again."
        isLoading={false}
      />
    );
  if (isPending) return <SplashScreen label="Setting up your workspace..." />;

  return null;
};

export default OnboardingPage;
