import RequestProcessedChart from '../tokens/request-processed-chart';

export const RequestProcessed = () => {
  return (
    <div className="full py-1 flex flex-col gap-4">
      <div className="flex-between">
        <h1 className="text-2xl">Request Processed</h1>
      </div>
      <div className="full mt-6">
        <RequestProcessedChart />
      </div>
    </div>
  );
};
