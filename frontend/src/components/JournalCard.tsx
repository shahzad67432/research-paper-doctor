interface Journal {
  name: string;
  topic: string;
  acceptance_rate: string;
  prestige: string;
  url: string;
  fit_score: number;
}

interface Props {
  journal: Journal;
}

function prestigeDots(prestige: string): string {
  if (prestige === "top") return "●●●";
  if (prestige === "high") return "●●○";
  return "●○○";
}

export function JournalCard({ journal }: Props) {
  return (
    <div className="bg-surface-high border border-border rounded-xl p-5">
      <h4 className="font-display font-semibold text-text-primary">
        {journal.name}
      </h4>
      <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs bg-accent/15 text-accent">
        {journal.topic}
      </span>
      <div className="mt-3 space-y-1 text-xs text-text-secondary">
        <div className="flex justify-between">
          <span>Acceptance Rate:</span>
          <span className="font-mono">{journal.acceptance_rate}</span>
        </div>
        <div className="flex justify-between">
          <span>Prestige:</span>
          <span className="text-gold tracking-wider">
            {prestigeDots(journal.prestige)}
          </span>
        </div>
      </div>
      <a
        href={journal.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-4 block w-full text-center py-2 rounded-lg border border-accent text-accent text-sm font-medium hover:bg-accent hover:text-canvas transition-colors"
      >
        Submit Paper →
      </a>
    </div>
  );
}
