import { Fira_Mono, Inter } from 'next/font/google';

export const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700', '800'],
});

export const firaMono = Fira_Mono({
  subsets: ['latin'],
  variable: '--font-fira-mono',
  display: 'swap',
  weight: ['400', '500', '700'],
});
