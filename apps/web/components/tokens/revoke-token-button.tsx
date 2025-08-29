import { Button } from '@hydra/ui/button';
import { Trash2 } from 'lucide-react';
import { useMutate } from '@/hooks/use-mutate';

type Props = {
  credentialId: string;
  orgId: string;
};

const RevokeTokenButton = ({ credentialId, orgId }: Props) => {
  const { mutateAsync, isPending, isSuccess } = useMutate();
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
    <Button className="w-14 center" disabled={isPending} onClick={handleRevoke}>
      <Trash2 size={20} className="text-red-400" />
    </Button>
  );
};

export default RevokeTokenButton;
