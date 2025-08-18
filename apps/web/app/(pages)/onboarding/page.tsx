'use client';

import { useRouter } from 'next/navigation';
import { useFetch } from '@/hooks/use-fetch';

type OnboardingData = {
  id: string;
  clerk_id: string;
  organization_id: string;
  created_at: string;
};

const OnboardingPage = () => {
  // Get userid from database, if it exists, redirect to /org/new
  // If it does not exist, initiate onboarding flow

  const { data, isLoading, error } = useFetch<OnboardingData>(
    ['onboarding'],
    '/onboarding',
    'POST'
  );
  const router = useRouter();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (data) {
    const { organization_id } = data;
    router.push(`/org/${organization_id}`);
    return null;
  }
};

export default OnboardingPage;
