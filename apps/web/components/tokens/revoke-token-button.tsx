import { Button } from '@hydra/ui/button';
import { useQueryClient } from '@tanstack/react-query';
import { Trash2 } from 'lucide-react';
import { useMutate } from '@/hooks/use-mutate';
import Spinner from './spinner';

type Props = {
  credentialId: string;
  orgId: string;
};

const RevokeTokenButton = ({ credentialId, orgId }: Props) => {
  const queryClient = useQueryClient();
  const { mutateAsync, isPending } = useMutate<
    void,
    unknown,
    { prevData: Credential[] | undefined }
  >({
    onMutate: async ({ url }) => {
      const credentialId = url.split('/').pop();

      await queryClient.cancelQueries({ queryKey: ['client_credentials'] });
      const prevData = queryClient.getQueryData<Credential[]>(['client_credentials']);

      queryClient.setQueryData<Credential[]>(['client_credentials'], old => {
        return old?.filter(cred => cred.id !== credentialId) ?? [];
      });

      return { prevData };
    },

    onError: (_err, _variables, context) => {
      if (context?.prevData) {
        queryClient.setQueryData(['client_credentials'], context.prevData);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['client_credentials'] });
    },
  });

  const handleRevoke = async () => {
    try {
      await mutateAsync({
        url: `/org/credentials/${orgId}/${credentialId}`,
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Failed to revoke token:', error);
    }
  };

  return (
    <Button
      className="w-14 center"
      disabled={isPending}
      onClick={handleRevoke}
      aria-label="Revoke Credential"
      title="Revoke Credential"
    >
      {isPending ? <Spinner /> : <Trash2 size={20} className="text-red-400" />}
    </Button>
  );
};

export default RevokeTokenButton;
