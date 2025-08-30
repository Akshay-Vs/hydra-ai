import Image from 'next/image';
import Link from 'next/link';
import Logo from '@/public/images/Hydra_Logo.svg';
import Spinner from './spinner';

type Props = {
  label?: string;
  isLoading?: boolean;
  showCredits?: boolean;
};

const SplashScreen = ({ label, isLoading = true, showCredits = true }: Props) => {
  return (
    <>
      <div className="screen z-[9999] absolute bg-background-dark inset-0 top-0 left-0 col-center gap-6">
        <Image src={Logo} alt="Hydra Logo" className="w-32 h-32 mx-auto mt-20" />
        <p className="text-text-dark/80">{label ?? 'Initializing...'}</p>
        {isLoading && <Spinner />}
      </div>
      {showCredits && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-center text-sm text-dull-dark/40 z-[10000]">
          <p>
            designed and developed by{' '}
            <Link
              href="https://akvs.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-primary"
            >
              akvs
            </Link>
          </p>
        </div>
      )}
    </>
  );
};

export default SplashScreen;
