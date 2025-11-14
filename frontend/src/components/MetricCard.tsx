type Props = {
  title: string;
  value: string;
  accent?: "default" | "success" | "warning";
};

const accentClassMap: Record<NonNullable<Props["accent"]>, string> = {
  default: "metric-value",
  success: "metric-value",
  warning: "metric-value"
};

const MetricCard = ({ title, value, accent = "default" }: Props) => {
  return (
    <div className="metric-card">
      <strong>{title}</strong>
      <span className={accentClassMap[accent]}>{value}</span>
    </div>
  );
};

export default MetricCard;

