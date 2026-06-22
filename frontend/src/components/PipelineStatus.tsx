"use client";

import { motion } from "framer-motion";

const STEPS = [
  "Parse PDF",
  "Analyze Structure",
  "Find Gaps",
  "Check Similarity",
  "Verify Citations",
  "Suggest Improvements",
  "Calculate Score",
  "Match Journals",
];

interface StepState {
  status: "idle" | "running" | "done" | "error";
  duration?: string;
}

interface Props {
  steps: StepState[];
}

export function PipelineStatus({ steps }: Props) {
  return (
    <div className="space-y-1">
      {STEPS.map((label, i) => {
        const s = steps[i] || { status: "idle" };
        return (
          <motion.div
            key={label}
            initial={s.status === "running" ? { x: -8, opacity: 0 } : undefined}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="flex items-center gap-3 py-1.5"
          >
            {/* Icon */}
            {s.status === "idle" && (
              <span className="w-4 h-4 rounded-full border border-text-muted" />
            )}
            {s.status === "running" && (
              <span className="w-4 h-4 rounded-full bg-accent animate-pulse" />
            )}
            {s.status === "done" && (
              <span className="w-4 h-4 rounded-full bg-mint flex items-center justify-center text-[10px] text-canvas font-bold">
                ✓
              </span>
            )}
            {s.status === "error" && (
              <span className="w-4 h-4 rounded-full bg-rose flex items-center justify-center text-[10px] text-canvas font-bold">
                ✕
              </span>
            )}
            <span className="font-mono text-sm text-text-secondary flex-1">
              {label}
            </span>
            {s.status === "running" && (
              <span className="font-mono text-xs text-accent">running...</span>
            )}
            {s.duration && s.status === "done" && (
              <span className="font-mono text-xs text-gold">{s.duration}</span>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}
