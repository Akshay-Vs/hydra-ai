import { useEffect } from 'react';
import { Button } from '@hydra/ui/button';
import { useQueryClient } from '@tanstack/react-query';
import { useMutate } from '@/hooks/use-mutate';
import { useModalStore } from '@/store/modal-store';
import { useOrgStore } from '@/store/org-store';
import ClientCredentialsModal from '../modals/client-credentials-modal';
import Spinner from './spinner';

type Credentials = {
  organization_id: string;
  client_secret: string;
  credential_id: string;
  expires_at: string;
};

const NewCredentialButton = () => {
  const queryClient = useQueryClient();
  const { data, isPending, mutateAsync } = useMutate<Credentials>({
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client_credentials'] });
    },
  });
  const { openModal, setTitle, setDescription, setContent } = useModalStore();
  const { selectedOrg } = useOrgStore();

  const handleOpen = async () => {
    await mutateAsync({
      url: '/org/credentials/generate',
      method: 'POST',
      data: {
        organization_id: selectedOrg?.id,
        expires_in: 90, // days
      },
    });
  };

  useEffect(() => {
    if (data) {
      const { expires_at: _, ...credentials } = data;

      setTitle('Client Credentials');
      setDescription('Copy and paste these credentials to your .env file.');

      setContent(<ClientCredentialsModal credentials={credentials} />);
      openModal();
    }
  }, [data, openModal, setContent, setDescription, setTitle]);

  return (
    <Button
      className="px-8 h-14 w-44 border-2 border-border-dark bg-surface-2-dark"
      onClick={handleOpen}
      disabled={isPending}
    >
      {isPending ? <Spinner /> : 'New Credential'}
    </Button>
  );
};

export default NewCredentialButton;
