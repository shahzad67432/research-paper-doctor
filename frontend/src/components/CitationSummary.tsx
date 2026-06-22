interface CitationResult {
  total: number;
  verified: number;
  matched: number;
  unmatched: number;
  invalid: string[];
  details: Array<{
    index: number;
    reference: string;
    status: string;
    doi: string | null;
    matched_title: string | null;
  }>;
}

interface Props {
  citations: CitationResult;
}

export function CitationSummary({ citations }: Props) {
  const { verified, matched, unmatched, invalid, details } = citations;
  return (
    <div>
      <div className="flex gap-3 mb-4">
        <span className="px-3 py-1 rounded-full bg-mint/15 text-mint text-xs font-mono">
          ✓ Verified: {verified}
        </span>
        <span className="px-3 py-1 rounded-full bg-amber/15 text-amber text-xs font-mono">
          ≈ Matched: {matched}
        </span>
        <span className="px-3 py-1 rounded-full bg-border text-text-secondary text-xs font-mono">
          ? Unmatched: {unmatched}
        </span>
      </div>
      {invalid.length > 0 && (
        <div className="bg-rose/10 border border-rose/30 rounded-lg p-4 mb-4">
          <p className="text-rose text-sm font-semibold mb-1">
            Invalid DOIs ({invalid.length})
          </p>
          <ul className="list-disc list-inside text-xs text-rose/80 space-y-0.5">
            {invalid.map((ref, i) => (
              <li key={i} className="truncate">{ref}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="space-y-1 font-mono text-xs max-h-60 overflow-y-auto">
        {details.map((d) => (
          <div
            key={d.index}
            className={`flex items-start gap-2 py-1 ${
              d.status === "verified"
                ? "text-mint"
                : d.status === "matched"
                  ? "text-amber"
                  : "text-text-secondary"
            }`}
          >
            <span className="shrink-0 mt-0.5">
              {d.status === "verified" ? "✓" : d.status === "matched" ? "≈" : "?"}
            </span>
            <span className="truncate">{d.reference.slice(0, 120)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
