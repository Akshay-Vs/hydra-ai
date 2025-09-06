'use client';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@hydra/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@hydra/ui/form';
import { Input } from '@hydra/ui/input';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useMutate } from '@/hooks/use-mutate';
import { useMCPServerStore } from '@/store/mcp-server-store';
import { useModalStore } from '@/store/modal-store';
import { useOrgStore } from '@/store/org-store';
import type { MCPServer } from '@/types/mcp-server';
import LoadingSpinner from '../tokens/loading-spinner';

const formSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().min(0).max(500, 'Description cannot exceed 500 characters'),
  icon: z.string().nullable(),
  url: z.url().min(1, 'URL is required'),
  auth_token: z.string().min(1, 'Auth token is required'),
});

type MCPFormData = z.infer<typeof formSchema>;

const MCPConfigModal = () => {
  const { closeModal } = useModalStore();
  const { selectedOrg } = useOrgStore();
  const { setMCPServers, mcp_servers } = useMCPServerStore();
  const { mutateAsync, isPending } = useMutate<MCPServer>({
    onSuccess: data => {
      setMCPServers([...mcp_servers, data]);
      closeModal();
    },
    onError: error => {
      console.error('Error creating MCP configuration:', error);
    },
  });

  const form = useForm<MCPFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      description: '',
      icon: '',
      url: '',
      auth_token: '',
    },
  });

  const onSubmit = async (data: MCPFormData) => {
    await mutateAsync({
      url: `/mcp/${selectedOrg?.id}`,
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
              <FormLabel className="text-base">Name</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder="MCP configuration name"
                  className="w-full p-4 py-6 my-2 border-2 border-active-dark rounded-2xl text-base placeholder:text-base"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="url"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">URL</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="url"
                  placeholder="https://example.com/mcp"
                  className="w-full p-4 py-6 my-2 border-2 border-active-dark rounded-2xl text-base placeholder:text-base"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="auth_token"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base">Auth Token</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="password"
                  placeholder="Authentication token"
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
              <FormLabel className="text-base">Description</FormLabel>
              <FormControl>
                <textarea
                  {...field}
                  placeholder="Brief description of the MCP configuration"
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
            {isPending ? <LoadingSpinner /> : 'Create MCP Config'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default MCPConfigModal;
