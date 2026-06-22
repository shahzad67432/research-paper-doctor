interface Paper {
  title: string;
  year: number;
  authors: string[];
  url: string;
  similarity_score: number;
  journal?: string;
}

interface Props {
  paper: Paper;
}

export function SimilarityCard({ paper }: Props) {
  const pct = Math.round((paper.similarity_score || 0) * 100);
  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h4 className="font-display font-semibold text-text-primary text-base">
            {paper.title}
          </h4>
          <p className="text-text-secondary text-sm mt-1">
            {paper.authors?.slice(0, 3).join(", ")} ({paper.year})
          </p>
        </div>
        <span className="font-mono text-2xl text-gold font-semibold ml-4">
          {pct}%
        </span>
      </div>
      <div className="mt-3 h-1 w-full bg-border rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-accent to-accent-bright transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      {paper.url && (
        <a
          href={paper.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-3 text-sm text-accent hover:underline"
        >
          View Paper →
        </a>
      )}
    </div>
  );
}
