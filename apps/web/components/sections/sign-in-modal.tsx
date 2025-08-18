import Image from 'next/image';
import { Connection, Loading } from '@clerk/elements/common';
import { Root } from '@clerk/elements/sign-in';
import { Button } from '@hydra/ui/button';
import { Loader } from 'lucide-react';
import { FaGithub, FaGoogle } from 'react-icons/fa';
import Logo from '@/public/images/Hydra_Logo.svg';
import Block from '../wrappers/block';

const SignInModal = () => {
  return (
    <Block className="w-[22dvw] col bg-transparent border-none">
      <div className="col-center gap-4">
        <Image
          src={Logo}
          height={48}
          width={48}
          alt="Hydra"
          className="h-12 w-12 object-center object-contain"
        />

        <h1 className="text-4xl">Hydra AI</h1>
      </div>
      <Root>
        <Loading>
          {isGlobalLoading => (
            <div className="col-center full gap-6">
              <Connection name="github" asChild>
                <Button disabled={isGlobalLoading} className="w-full h-12">
                  <Loading scope="provider:github">
                    {isLoading => (isLoading ? <Loader /> : <FaGithub className="text-xl" />)}
                  </Loading>
                </Button>
              </Connection>

              <Connection name="google" asChild>
                <Button disabled={isGlobalLoading} className="w-full h-12">
                  <Loading scope="provider:google">
                    {isLoading => (isLoading ? <Loader /> : <FaGoogle className="text-xl" />)}
                  </Loading>
                </Button>
              </Connection>
              <div id="clerk-captcha" />
            </div>
          )}
        </Loading>
      </Root>
    </Block>
  );
};

export default SignInModal;
