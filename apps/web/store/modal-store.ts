import type { ReactElement, ReactNode } from 'react';
import { create } from 'zustand';

interface ModalStore {
  isOpen: boolean;
  title: string;
  description?: string;
  content: ReactNode | ReactElement;
  setContent: (content: ReactNode | ReactElement | null) => void;
  setTitle: (title: string) => void;
  setDescription: (description: string) => void;
  openModal: () => void;
  closeModal: () => void;
}

export const useModalStore = create<ModalStore>(set => ({
  isOpen: false,
  content: null,
  title: '',
  description: '',
  openModal: () => set({ isOpen: true }),
  closeModal: () => set({ isOpen: false }),
  setContent: (content: ReactNode | ReactElement) => set({ content }),
  setTitle: (title: string) => set({ title }),
  setDescription: (description: string) =>
    set({
      description,
    }),
}));
