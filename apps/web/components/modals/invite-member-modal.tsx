import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@hydra/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@hydra/ui/form';
import { Input } from '@hydra/ui/input';
import { useForm } from 'react-hook-form';
import z from 'zod';
import { useMutate } from '@/hooks/use-mutate';
import LoadingSpinner from '../tokens/loading-spinner';

const formSchema = z.object({
  recipient_email: z.string(),
  role_id: z.string(),
  message: z.string().optional(),
  expires_at: z.string().optional(),
});

const InviteMemberModal = () => {
  const { isPending } = useMutate();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      recipient_email: '',
      role_id: '',
      message: '',
      expires_at: '',
    },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    console.log(data);
  };
  return (
    <Form {...form}>
      <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="recipient_email"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Recipient Email</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="email"
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
          name="expires_at"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Expires At</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder="Brief description of the organization"
                  className="w-full p-4 py-6 my-2 border-2 border-active-dark rounded-2xl text-base placeholder:text-base"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Invitation Message</FormLabel>
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
            {isPending ? <LoadingSpinner /> : 'Send Invitation'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default InviteMemberModal;
