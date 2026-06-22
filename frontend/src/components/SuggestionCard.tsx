interface Suggestion {
  priority: string;
  action: string;
  estimated_effort: string;
  expected_impact: string;
}

interface Props {
  suggestion: Suggestion;
}

const priorityConfig: Record<string, { color: string; label: string }> = {
  high: { color: "#F87171", label: "High Priority" },
  medium: { color: "#FBBF24", label: "Medium" },
  low: { color: "#34D399", label: "Low" },
};

export function SuggestionCard({ suggestion }: Props) {
  const cfg = priorityConfig[suggestion.priority] || priorityConfig.medium;
  return (
    <div className="mb-4">
      <div className="flex items-start gap-3 bg-surface-high border border-border rounded-lg p-4">
        <span
          className="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0"
          style={{ backgroundColor: cfg.color }}
        />
        <div className="flex-1">
          <p className="text-text-primary font-semibold text-sm">
            {suggestion.action}
          </p>
          <div className="flex gap-2 mt-2">
            <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface text-text-secondary">
              ⏱ {suggestion.estimated_effort}
            </span>
            <span className="px-2 py-0.5 rounded text-xs font-mono bg-surface text-text-secondary">
              ↑ {suggestion.expected_impact}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
