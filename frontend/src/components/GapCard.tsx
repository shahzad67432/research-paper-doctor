interface Gap {
  title: string;
  year: number;
  url: string;
  gap_type: string;
  gap_description: string;
  why_you_can_fill_it: string;
  _note?: string;
}

interface Props {
  gap: Gap;
}

const severityColor: Record<string, string> = {
  methodology: "border-rose",
  analysis: "border-rose",
  literature: "border-accent",
  results: "border-amber",
  conclusion: "border-accent",
};

export function GapCard({ gap }: Props) {
  const border = severityColor[gap.gap_type] || "border-accent";
  return (
    <div className={`border-l-4 ${border} bg-surface-high rounded-lg p-5 mb-3`}>
      <div className="flex items-center gap-2">
        <span className="font-mono text-xs uppercase text-text-secondary">
          {gap.gap_type}
        </span>
      </div>
      <p className="text-text-primary text-sm mt-2 leading-relaxed">
        {gap.gap_description}
      </p>
      {gap.why_you_can_fill_it && (
        <p className="mt-3 text-sm text-accent-bright italic">
          💡 {gap.why_you_can_fill_it}
        </p>
      )}
      {gap._note && (
        <p className="mt-2 text-xs text-amber font-mono">{gap._note}</p>
      )}
    </div>
  );
}
