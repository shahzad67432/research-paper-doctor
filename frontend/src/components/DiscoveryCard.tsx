interface Discovery {
  title: string;
  year: number;
  url: string;
  gap_type: string;
  gap_description: string;
  why_you_can_fill_it: string;
  _note?: string;
}

interface Props {
  item: Discovery;
}

export function DiscoveryCard({ item }: Props) {
  return (
    <div className="border-l-[3px] border-accent bg-surface rounded-xl p-6">
      <p className="font-mono text-xs text-text-secondary uppercase tracking-widest">
        Research Opportunity
      </p>
      <h3 className="font-display font-semibold text-text-primary text-lg mt-1">
        {item.title}
      </h3>
      <p className="text-text-secondary text-sm">{item.year}</p>
      <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs bg-accent/15 text-accent">
        {item.gap_type}
      </span>
      <p className="text-text-primary text-sm mt-3 leading-relaxed">
        {item.gap_description}
      </p>
      {item.why_you_can_fill_it && (
        <p className="text-accent-bright text-sm mt-2 italic">
          💡 {item.why_you_can_fill_it}
        </p>
      )}
      {item._note && (
        <p className="mt-2 text-xs text-amber font-mono">{item._note}</p>
      )}
      {item.url && (
        <a
          href={item.url}
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
