'use client';

import { useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import SignInModal from '@/components/sections/sign-in-modal';

export default function SignInPage() {
  const { isSignedIn } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isSignedIn) {
      router.push('/');
    }
  }, [isSignedIn, router]);

  return (
    <div className="screen center relative">
      <SignInModal />
      <div className="absolute top-0 right-0 screen overflow-hidden rounded-l-4xl -z-10">
        <Image
          src="https://mlgktt2y6f.ufs.sh/f/6YinM32zuOKMUFK3WuptXYSM4ykirLZAm75DThCo9xsBGaRI"
          alt="Welcome to Hydra AI"
          height={1440}
          width={1440}
          className="full object-center object-cover brightness-50"
        />
      </div>
    </div>
  );
}
