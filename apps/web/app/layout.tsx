import type { Metadata, Viewport } from 'next';

import '@/styles/globals.scss';
import '@/styles/tailwind.css';
import '@hydra/ui/styles.css';

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
    <html lang="en" data-theme="dark">
      <body
        className={`${inter.variable} ${firaMono.variable} antialiased bg-background-dark dark:text-text-dark`}
      >
        {children}
      </body>
    </html>
  );
}
