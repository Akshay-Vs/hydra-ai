import React from 'react';
import type { Metadata, Viewport } from 'next';
import { ClerkProvider } from '@clerk/nextjs';

import '@/styles/globals.scss';
import '@/styles/tailwind.css';
import '@hydra/ui/styles.css';

import { Providers } from '@/components/wrappers/providers';
import { firaMono, inter } from './(global)/fonts';
import { HydraMetadata, HydraViewport } from './(global)/metadata';

export const metadata: Metadata = HydraMetadata;
export const viewport: Viewport = HydraViewport;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" data-theme="dark">
        <body
          className={`${inter.variable} ${firaMono.variable} antialiased bg-background-dark dark:text-text-dark`}
        >
          <Providers>{children}</Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
