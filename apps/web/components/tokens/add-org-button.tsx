import { Button } from '@hydra/ui/button';
import { useModalStore } from '@/store/modal-store';
import CreateOrgModal from '../modals/create-org-modal';

const AddOrgButton = () => {
  const { openModal, setTitle, setDescription, setContent } = useModalStore();

  const handleOpen = () => {
    setTitle('Create Organization');
    setDescription('Create a new organization');
    openModal();
    setContent(<CreateOrgModal />);
  };

  return (
    <Button
      size="default"
      variant="default"
      className="rounded-lg text-base font-bold hover:bg-active-dark"
      onClick={handleOpen}
    >
      Create New
    </Button>
  );
};

export default AddOrgButton;
