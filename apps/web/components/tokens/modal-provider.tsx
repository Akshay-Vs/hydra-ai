'use client';

import type { MouseEvent } from 'react';
import { X } from 'lucide-react';
import { useModalStore } from '@/store/modal-store';
import Block from '../wrappers/block';

const ModalProvider = () => {
  const { isOpen, closeModal, title, description, content } = useModalStore();

  if (!isOpen) return null;

  return (
    <div className="absolute bg-black/20 screen center top-0% left-0 z-[999]" onClick={closeModal}>
      <Block
        className="min-h-52 h-fit w-[32vw] justify-start items-start bg-background-dark"
        onClick={(e: MouseEvent<HTMLDivElement>) => e.stopPropagation()}
      >
        <div className="p-4 pt-2 col full">
          <div className="flex justify-between items-center">
            {title && <h2 className="text-2xl mb-2">{title}</h2>}
            <button className="p-2 cursor-pointer" onClick={closeModal}>
              <X />
            </button>
          </div>
          {description && <p className="text-base text-muted-foreground mb-4">{description}</p>}
          <div className="content">{content}</div>
        </div>
      </Block>
    </div>
  );
};

export default ModalProvider;
