export type LogEntry = {
  id: string;
  timestamp: string;
  source: {
    name: string;
    color: string;
  };
  message: {
    text: string;
    color: string;
  };
};
