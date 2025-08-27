import Image from 'next/image';
import Logo from '@/public/images/Hydra_Logo.svg';
import Spinner from './spinner';

type Props = {
  label?: string;
  isLoading?: boolean;
};

const SplashScreen = ({ label, isLoading = true }: Props) => {
  return (
    <div className="absolute inset-0 top-0 left-0 col-center gap-6 bg-background-dark">
      <Image src={Logo} alt="Hydra Logo" className="w-32 h-32 mx-auto mt-20" />
      <p className="text-text-dark/80">{label ?? 'Initializing...'}</p>
      {isLoading ?? <Spinner />}{' '}
    </div>
  );
};

export default SplashScreen;
