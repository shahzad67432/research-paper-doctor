interface Props {
  label: string;
  value: number;
  color?: string;
}

export function MetricCard({ label, value, color }: Props) {
  const textColor = color || (value < 40 ? "#F87171" : value < 70 ? "#FBBF24" : "#34D399");
  return (
    <div className="bg-surface-high border border-border-subtle p-4 rounded-lg">
      <div className="font-mono text-2xl font-semibold" style={{ color: textColor }}>
        {value}
      </div>
      <div className="text-xs text-text-secondary uppercase tracking-wide mt-1">
        {label}
      </div>
    </div>
  );
}
