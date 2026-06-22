"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Loader2, CheckCircle2, XCircle, Circle } from "lucide-react";

type Mode = "analyze" | "qa" | "discover";
type StepStatus = "idle" | "running" | "done" | "error";

interface Step {
  id: string;
  label: string;
  sub?: string;
  status: StepStatus;
}

const PIPELINES: Record<Mode, Step[]> = {
  analyze: [
    { id: "parse", label: "Parse PDF", sub: "Extract text, sections, references", status: "idle" },
    { id: "structure", label: "Analyze Structure", sub: "Detect topic, word counts, section quality", status: "idle" },
    { id: "gaps", label: "Find Gaps", sub: "LLM identifies missing elements", status: "idle" },
    { id: "similarity", label: "Check Similarity", sub: "arXiv · PubMed · OpenAlex · Embedding search", status: "idle" },
    { id: "citations", label: "Verify Citations", sub: "Crossref DOI check + bibliographic match", status: "idle" },
    { id: "suggestions", label: "Improvement Suggestions", sub: "LLM generates actionable improvements", status: "idle" },
    { id: "score", label: "Calculate Score", sub: "0–100 readiness score", status: "idle" },
    { id: "journals", label: "Match Journals", sub: "Embedding similarity to 46 journals", status: "idle" },
  ],
  qa: [
    { id: "rag", label: "RAG Cache Search", sub: "Search cached papers (ChromaDB)", status: "idle" },
    { id: "live", label: "Live Search", sub: "arXiv + OpenAlex fetch", status: "idle" },
    { id: "context", label: "Build Context", sub: "Top-8 papers, 1500 char limit", status: "idle" },
    { id: "llm", label: "LLM Answer Generation", sub: "Gemini → OpenRouter fallback", status: "idle" },
  ],
  discover: [
    { id: "rag", label: "RAG Cache Search", sub: "Search cached papers (ChromaDB)", status: "idle" },
    { id: "live", label: "Live Search", sub: "arXiv + OpenAlex fetch", status: "idle" },
    { id: "llm", label: "LLM Gap Analysis", sub: "Gemini → OpenRouter fallback", status: "idle" },
    { id: "fallback", label: "Fallback", sub: "Generic gap text if LLM unavailable", status: "idle" },
  ],
};

const MODE_LABELS: Record<Mode, string> = {
  analyze: "Paper Analysis Pipeline",
  qa: "Q&A Pipeline",
  discover: "Gap Discovery Pipeline",
};

const MODE_COLORS: Record<Mode, string> = {
  analyze: "#5B8DEF",
  qa: "#34D399",
  discover: "#E8B84B",
};

const STATUS_ICON: Record<StepStatus, React.ReactNode> = {
  idle: <Circle size={16} className="text-text-muted" />,
  running: <Loader2 size={16} className="text-accent animate-spin" />,
  done: <CheckCircle2 size={16} className="text-mint" />,
  error: <XCircle size={16} className="text-rose" />,
};

export default function PipelinePage() {
  const [mode, setMode] = useState<Mode>("analyze");
  const [steps, setSteps] = useState<Step[]>(PIPELINES.analyze);
  const [demoRunning, setDemoRunning] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const runDemo = useCallback(async () => {
    setDemoRunning(true);
    const pipeline = PIPELINES[mode];
    setSteps(pipeline.map((s, i) => ({
      ...s,
      status: i === 0 ? "running" as const : "idle" as const,
    })));

    for (let i = 0; i < pipeline.length; i++) {
      await new Promise((r) => setTimeout(r, 600 + Math.random() * 900));
      setSteps((prev) => prev.map((s, j) => ({
        ...s,
        status: j === i ? "done" as const : j === i + 1 ? "running" as const : s.status,
      })));
    }
    setDemoRunning(false);
  }, [mode]);

  const handleModeChange = useCallback((m: Mode) => {
    setMode(m);
    setSteps(PIPELINES[m].map((s) => ({ ...s, status: "idle" as const })));
    if (intervalRef.current) clearInterval(intervalRef.current);
  }, []);

  useEffect(() => {
    const id = intervalRef.current;
    return () => {
      if (id) clearInterval(id);
    };
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <h1 className="font-display font-semibold text-text-primary text-xl">
          Pipeline Explorer
        </h1>
        <div className="flex gap-1.5 ml-auto">
          {(["analyze", "qa", "discover"] as Mode[]).map((m) => (
            <button
              key={m}
              onClick={() => handleModeChange(m)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium font-display transition-all ${
                mode === m
                  ? "text-canvas"
                  : "text-text-secondary hover:text-text-primary bg-surface-high"
              }`}
              style={mode === m ? { backgroundColor: MODE_COLORS[m] } : undefined}
            >
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Two-column layout */}
      <div className="flex gap-6">
        {/* Pipeline visualization */}
        <div className="flex-1 bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-display font-semibold text-text-primary text-base">
              {MODE_LABELS[mode]}
            </h2>
            <div className="flex items-center gap-2">
              {!demoRunning && (
                <button
                  onClick={runDemo}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent/15 text-accent text-xs font-medium hover:bg-accent/25 transition-colors"
                >
                  <Play size={12} />
                  Run Demo
                </button>
              )}
              <span
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: demoRunning ? MODE_COLORS[mode] : "#364860",
                  animation: demoRunning ? "pulse 1.5s infinite" : "none",
                }}
              />
            </div>
          </div>

          {/* Pipeline steps */}
          <div className="relative">
            {/* Vertical connecting line */}
            <div
              className="absolute left-[7px] top-2 bottom-2 w-0.5"
              style={{
                background: `linear-gradient(to bottom, ${MODE_COLORS[mode]}55, ${MODE_COLORS[mode]}33)`,
              }}
            />

            <div className="space-y-0">
              {steps.map((step, i) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06, duration: 0.2 }}
                  className="relative flex items-start gap-4 pb-6"
                >
                  {/* Status icon */}
                  <motion.div
                    layout
                    className="relative z-10 mt-0.5"
                    animate={{
                      scale: step.status === "running" ? [1, 1.2, 1] : 1,
                    }}
                    transition={{ duration: 0.8, repeat: step.status === "running" ? Infinity : 0 }}
                  >
                    {STATUS_ICON[step.status]}
                  </motion.div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div
                      className={`font-display font-semibold text-sm transition-colors duration-300 ${
                        step.status === "done"
                          ? "text-mint"
                          : step.status === "running"
                            ? "text-accent"
                            : step.status === "error"
                              ? "text-rose"
                              : "text-text-primary"
                      }`}
                    >
                      {step.label}
                    </div>
                    {step.sub && (
                      <div className="text-[11px] font-mono text-text-muted mt-0.5">
                        {step.sub}
                      </div>
                    )}

                    {/* Animated progress bar for running steps */}
                    <AnimatePresence>
                      {step.status === "running" && (
                        <motion.div
                          initial={{ scaleX: 0 }}
                          animate={{ scaleX: 1 }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="origin-left h-0.5 mt-1.5 rounded-full"
                          style={{ backgroundColor: MODE_COLORS[mode] }}
                        />
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Step number badge */}
                  <span className="font-mono text-[10px] text-text-muted">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Side panel — Legend + Status */}
        <div className="w-72 shrink-0 space-y-4">
          {/* Legend */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="font-display font-semibold text-text-primary text-sm mb-3">
              Legend
            </h3>
            <div className="space-y-2 text-xs font-mono text-text-secondary">
              {[
                { icon: <Circle size={12} />, label: "Idle — waiting" },
                { icon: <Loader2 size={12} className="animate-spin text-accent" />, label: "Running — in progress" },
                { icon: <CheckCircle2 size={12} className="text-mint" />, label: "Done — completed" },
                { icon: <XCircle size={12} className="text-rose" />, label: "Error — failed" },
              ].map(({ icon, label }) => (
                <div key={label} className="flex items-center gap-2">
                  {icon}
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Pipeline info */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="font-display font-semibold text-text-primary text-sm mb-3">
              Pipeline Info
            </h3>
            <div className="space-y-2 text-xs font-mono text-text-secondary">
              <div className="flex justify-between">
                <span>Mode</span>
                <span className="text-text-primary capitalize">{mode}</span>
              </div>
              <div className="flex justify-between">
                <span>Steps</span>
                <span className="text-text-primary">{steps.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Completed</span>
                <span className="text-mint">
                  {steps.filter((s) => s.status === "done").length}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Errors</span>
                <span className="text-rose">
                  {steps.filter((s) => s.status === "error").length}
                </span>
              </div>
            </div>
          </div>

          {/* Model info */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h3 className="font-display font-semibold text-text-primary text-sm mb-3">
              LLM & Data Sources
            </h3>
            <div className="space-y-2 text-xs font-mono text-text-secondary">
              {[
                ["Primary LLM", "gemini-1.5-flash"],
                ["Fallback LLM", "qwen/qwen3-coder:free"],
                ["RAG DB", "ChromaDB (all-MiniLM-L6-v2)"],
                ["Paper Sources", "arXiv · OpenAlex · PubMed"],
                ["Citation DB", "Crossref"],
              ].map(([k, v]) => (
                <div key={k}>
                  <span>{k}</span>
                  <div className="text-text-primary truncate">{v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Try it button */}
          <button
            onClick={runDemo}
            disabled={demoRunning}
            className="w-full py-2.5 rounded-lg font-display font-semibold text-sm text-canvas bg-gradient-to-r from-accent to-accent-bright hover:brightness-110 transition-all disabled:opacity-50"
          >
            {demoRunning ? "Running..." : `Run ${mode} Demo →`}
          </button>
        </div>
      </div>
    </div>
  );
}
