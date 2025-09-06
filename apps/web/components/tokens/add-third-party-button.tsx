'use client';
import { Button } from '@hydra/ui/button';
import { useModalStore } from '@/store/modal-store';
import ThirdPartyModal from '../modals/third-party-modal';

const AddThirdPartyButton = () => {
  const { openModal, setTitle, setDescription, setContent } = useModalStore();
  const handleOpen = () => {
    setTitle('Add MCP Configuration');
    setDescription('Add a new MCP Server configuration');
    setContent(<ThirdPartyModal />);
    openModal();
  };
  return (
    <Button
      className="px-8 h-14 w-52 border-2 border-border-dark bg-surface-2-dark z-50"
      onClick={handleOpen}
    // disabled={isPending}
    >
      {
        // isPending ? <Spinner /> :
        'Add MCP Server'
      }
    </Button>
  );
};

export default AddThirdPartyButton;
