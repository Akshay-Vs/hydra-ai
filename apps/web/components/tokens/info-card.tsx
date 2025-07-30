type Props = {
  title: string;
  description: string;
  value: string;
};

const InfoCard = ({ title, description, value }: Props) => {
  return (
    <div className="full p-4 bg-surface-3-dark center rounded-default gap-4">
      <div className="col gap-4">
        <h3 className="text-2xl font-[400]">{title}</h3>
        <p className="text-sm text-dull-dark/75">{description}</p>
      </div>
      <p className="text-6xl font-light">{value}</p>
    </div>
  );
};

export default InfoCard;
