import { Button } from '@hydra/ui/button';
import { useModalStore } from '@/store/modal-store';
import InviteMemberModal from '../modals/invite-member-modal';

const InviteMemberButton = () => {
  const { setTitle, setDescription, setContent, openModal } = useModalStore();

  const handleClick = () => {
    setTitle('Invite Member');
    setDescription('Send Invite to a team member');
    setContent(<InviteMemberModal />);
    openModal();
  };
  return (
    <Button variant="secondary" className="h-full" size="default" onClick={handleClick}>
      Invite Members
    </Button>
  );
};

export default InviteMemberButton;
