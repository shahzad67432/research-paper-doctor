"use client";

interface Props {
  score: number;
}

function scoreColor(score: number): string {
  if (score < 40) return "#F87171";
  if (score < 70) return "#FBBF24";
  return "#34D399";
}

export function ReadinessRing({ score }: Props) {
  const r = 80;
  const stroke = 8;
  const normalizedRadius = r - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  const color = scoreColor(score);

  return (
    <div className="flex flex-col items-center">
      <svg width={r * 2} height={r * 2} className="transform -rotate-90">
        <circle
          cx={r}
          cy={r}
          r={normalizedRadius}
          fill="none"
          stroke="#1E2D44"
          strokeWidth={stroke}
        />
        <circle
          cx={r}
          cy={r}
          r={normalizedRadius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ width: r * 2, height: r * 2 }}>
        <span className="font-display text-5xl font-bold text-gold">
          {score}
        </span>
        <span className="text-text-secondary text-sm">/ 100</span>
      </div>
      <span className="mt-4 font-display text-sm text-secondary uppercase tracking-widest">
        Publication Readiness
      </span>
    </div>
  );
}
