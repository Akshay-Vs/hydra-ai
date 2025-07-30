import InfoCard from '../tokens/info-card';

const InfoBlock = () => {
  const data = [
    {
      title: 'Auto Fixed',
      description:
        'Issues resolved autonomously by the agent with high confidence and no human input',
      value: '235',
    },
    {
      title: 'Pending Requests',
      description: 'Agent attempted a fix but flagged for human review due to low confidence',
      value: '123',
    },
    {
      title: 'Escalated Issues',
      description: 'Agent failed to resolve and escalated the issue for manual intervention',
      value: '08',
    },
  ];
  return (
    <div className="full col gap-4">
      {data.map((item, index) => (
        <InfoCard
          key={index}
          title={item.title}
          description={item.description}
          value={item.value}
        />
      ))}
    </div>
  );
};

export default InfoBlock;
