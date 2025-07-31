import type { Metadata, Viewport } from 'next';

const APP_NAME = 'Hydra';
const APP_DEFAULT_TITLE = 'Hydra AI - Devops Agentic AI Assistant';
const APP_TITLE_TEMPLATE = '%s - Hydra AI';
const APP_DESCRIPTION = 'Hydra AI is a DevOps agentic AI assistant';

export const HydraMetadata: Metadata = {
  applicationName: APP_NAME,
  title: {
    default: APP_DEFAULT_TITLE,
    template: APP_TITLE_TEMPLATE,
  },
  description: APP_DESCRIPTION,
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: APP_DEFAULT_TITLE,
    // startUpImage: [],
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    type: 'website',
    siteName: APP_NAME,
    title: {
      default: APP_DEFAULT_TITLE,
      template: APP_TITLE_TEMPLATE,
    },
    description: APP_DESCRIPTION,
  },
  twitter: {
    card: 'summary',
    title: {
      default: APP_DEFAULT_TITLE,
      template: APP_TITLE_TEMPLATE,
    },
    description: APP_DESCRIPTION,
  },
};
export const HydraViewport: Viewport = {
  themeColor: '#30363A',
};
