'use client';
import { useRouter } from 'next/navigation';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@hydra/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@hydra/ui/form';
import { Input } from '@hydra/ui/input';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useMutate } from '@/hooks/use-mutate';
import { useModalStore } from '@/store/modal-store';
import type { Organization } from '@/types/org';
import LoadingSpinner from '../tokens/loading-spinner';

const formSchema = z.object({
  name: z.string().min(1, 'Organization name is required'),
  description: z.string().min(0).max(500, 'Description cannot exceed 500 characters'),
});

const CreateOrgModal = () => {
  const router = useRouter();
  const { closeModal } = useModalStore();

  const { mutateAsync, isPending } = useMutate<Organization>({
    onSuccess: org => {
      router.push(`/org/${org.id}`);
      closeModal();
      setTimeout(() => router.push(`/org/${org.id}`), 80);
    },
    onError: error => {
      // Handle error, e.g., show an error message
      console.error('Error creating organization:', error);
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      description: '',
    },
  });
  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    await mutateAsync({
      url: '/org',
      method: 'POST',
      data,
    });
  };

  return (
    <Form {...form}>
      <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Organization Name</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder="Name of the organization"
                  className="w-full p-4 py-6 my-2 border-2 border-active-dark rounded-2xl text-base placeholder:text-base"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Organization Description</FormLabel>
              <FormControl>
                <textarea
                  {...field}
                  placeholder="Brief description of the organization"
                  className="w-full p-4 py-4 h-32 my-2 border-2 placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none border-active-dark rounded-2xl text-base placeholder:text-base"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="w-full flex justify-end">
          <Button
            variant="secondary"
            size="lg"
            className="rounded-xl py-6 w-48"
            disabled={isPending}
          >
            {isPending ? <LoadingSpinner /> : 'Create Organization'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default CreateOrgModal;
