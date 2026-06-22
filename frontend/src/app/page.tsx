"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as Tabs from "@radix-ui/react-tabs";
import { UploadZone } from "@/components/UploadZone";
import { PipelineStatus } from "@/components/PipelineStatus";
import { ReadinessRing } from "@/components/ReadinessRing";
import { MetricCard } from "@/components/MetricCard";
import { GapCard } from "@/components/GapCard";
import { SimilarityCard } from "@/components/SimilarityCard";
import { CitationSummary } from "@/components/CitationSummary";
import { SuggestionCard } from "@/components/SuggestionCard";
import { JournalCard } from "@/components/JournalCard";
import { uploadPaper, getJobStatus } from "@/lib/api";
import type { JobStatus } from "@/lib/api";

const PIPELINE_STEPS = [
  "Parse PDF",
  "Analyze Structure",
  "Find Gaps",
  "Check Similarity",
  "Verify Citations",
  "Suggest Improvements",
  "Calculate Score",
  "Match Journals",
];

type StepState = { status: "idle" | "running" | "done" | "error"; duration?: string };

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [steps, setSteps] = useState<StepState[]>(
    PIPELINE_STEPS.map(() => ({ status: "idle" })),
  );
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const poll = useCallback((id: string) => {
    intervalRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(id);
        setJob(status);
        if (status.status === "done" || status.status === "error") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setLoading(false);
        }
      } catch {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setLoading(false);
      }
    }, 1500);
  }, []);

  // Animate pipeline steps optimistically
  useEffect(() => {
    if (!loading) return;
    setSteps(PIPELINE_STEPS.map(() => ({ status: "idle" })));
    const delays = [500, 3000, 6000, 9000, 12000, 16000, 20000, 24000];
    const timeouts: ReturnType<typeof setTimeout>[] = [];

    PIPELINE_STEPS.forEach((_, i) => {
      timeouts.push(
        setTimeout(() => {
          setSteps((prev) => {
            const next = [...prev];
            if (i > 0) next[i - 1] = { ...next[i - 1], status: "done", duration: `${((delays[i] - delays[i - 1]) / 1000).toFixed(1)}s` };
            next[i] = { ...next[i], status: "running" };
            return next;
          });
        }, delays[i]),
      );
    });

    // Mark last step done after final delay
    timeouts.push(
      setTimeout(() => {
        setSteps((prev) => {
          const next = [...prev];
          next[next.length - 1] = { ...next[next.length - 1], status: "done", duration: "3.2s" };
          return next;
        });
      }, delays[delays.length - 1] + 3000),
    );

    return () => timeouts.forEach(clearTimeout);
  }, [loading]);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setJob(null);
    try {
      const { job_id } = await uploadPaper(file);
      poll(job_id);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  }, [file, poll]);

  const result = job?.result as Record<string, unknown> | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const structure = result?.structure as Record<string, any> | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const gaps = (result?.gaps as any[]) || [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const similar = (result?.similar_papers as any[]) || [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const citations = result?.citation_results as Record<string, any> | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const improvements = (result?.improvements as any[]) || [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const score = result?.readiness_score as Record<string, any> | undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const journals = (result?.journal_matches as any[]) || [];
  const scores = (score?.breakdown || {}) as Record<string, number>;

  const sectionPresent = (s: string) => {
    const secs = structure?.sections as string[] | undefined;
    return secs?.some((x: string) => x.toLowerCase().includes(s.toLowerCase()));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left column */}
        <div className="w-full lg:w-[380px] shrink-0 space-y-6">
          <div className="bg-surface border border-border rounded-xl p-6">
            <UploadZone file={file} onFile={setFile} />
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="mt-4 w-full h-12 rounded-lg font-display font-semibold text-canvas bg-gradient-to-r from-accent to-accent-bright hover:brightness-110 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(91,141,239,0.27)] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-canvas border-t-transparent rounded-full animate-spin" />
                  Analyzing...
                </span>
              ) : (
                "Analyze Paper"
              )}
            </button>
            <p className="mt-2 text-text-muted font-mono text-xs text-center">
              ~30-60s · arXiv · PubMed · OpenAlex · CrossRef
            </p>
          </div>

          {/* Pipeline status */}
          {(loading || job?.status === "done" || job?.status === "error") && (
            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="font-display font-semibold text-text-primary text-sm mb-3">
                Pipeline Status
              </h3>
              <PipelineStatus steps={steps} />
            </div>
          )}
        </div>

        {/* Right column — results */}
        <div className="flex-1 min-w-0">
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-surface border border-border rounded-xl p-6"
              >
                <Tabs.Root defaultValue="overview">
                  <Tabs.List className="flex gap-1 border-b border-border pb-0 mb-6 overflow-x-auto">
                    {["Overview", "Gaps", "Similarity", "Citations", "Suggestions", "Journals"].map(
                      (tab) => (
                        <Tabs.Trigger
                          key={tab}
                          value={tab.toLowerCase()}
                          className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary data-[state=active]:text-accent data-[state=active]:border-b-2 data-[state=active]:border-accent transition-colors whitespace-nowrap"
                        >
                          {tab}
                        </Tabs.Trigger>
                      ),
                    )}
                  </Tabs.List>

                  {/* Overview */}
                  <Tabs.Content value="overview" className="space-y-6">
                    {score && (
                      <div className="flex flex-col items-center">
                        <div className="relative">
                          <ReadinessRing score={score.score || 0} />
                        </div>
                        <div className="grid grid-cols-2 gap-3 w-full max-w-md mt-6">
                          <MetricCard label="Methodology" value={scores.methodology || 0} />
                          <MetricCard label="Novelty" value={scores.novelty || 0} />
                          <MetricCard label="Citations" value={scores.citations || 0} />
                          <MetricCard label="Writing" value={scores.writing || 0} />
                        </div>
                      </div>
                    )}

                    {structure && (
                      <>
                        <div>
                          <h4 className="font-display font-semibold text-text-primary text-sm mb-3">
                            Section Presence
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {["Abstract", "Introduction", "Methods", "Results", "Conclusion", "References"].map(
                              (s) => (
                                <span
                                  key={s}
                                  className={`px-3 py-1 rounded-full text-xs font-mono ${
                                    sectionPresent(s)
                                      ? "bg-mint/15 text-mint border border-mint/30"
                                      : "bg-transparent text-rose border border-rose/40"
                                  }`}
                                >
                                  {s}
                                </span>
                              ),
                            )}
                          </div>
                        </div>
                        {structure.word_counts && (
                          <div>
                            <h4 className="font-display font-semibold text-text-primary text-sm mb-3">
                              Word Counts
                            </h4>
                            <div className="space-y-2">
                              {Object.entries(structure.word_counts as Record<string, number>).map(
                                ([key, count]) => {
                                  const vals = Object.values(structure?.word_counts || {}) as number[];
                                  const max = Math.max(...vals, 1);
                                  return (
                                    <div key={key} className="flex items-center gap-3">
                                      <span className="font-mono text-xs text-text-secondary w-28 truncate">
                                        {key}
                                      </span>
                                      <div className="flex-1 h-3 bg-border rounded-full overflow-hidden">
                                        <div
                                          className="h-full rounded-full bg-accent/60 transition-all duration-500"
                                          style={{ width: `${(count / max) * 100}%` }}
                                        />
                                      </div>
                                      <span className="font-mono text-xs text-text-secondary w-16 text-right">
                                        {count}
                                      </span>
                                    </div>
                                  );
                                },
                              )}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </Tabs.Content>

                  {/* Gaps */}
                  <Tabs.Content value="gaps">
                    {gaps.length === 0 ? (
                      <p className="text-text-secondary text-sm">No gaps identified.</p>
                    ) : (
                      <div className="space-y-3">
                        {gaps.map((g: any, i: number) => (
                          <GapCard key={i} gap={g} />
                        ))}
                      </div>
                    )}
                  </Tabs.Content>

                  {/* Similarity */}
                  <Tabs.Content value="similarity">
                    <p className="text-text-secondary text-xs font-mono mb-4">
                      Semantic similarity via sentence-transformers · Sources: arXiv, PubMed, OpenAlex
                    </p>
                    {similar.length === 0 ? (
                      <p className="text-text-secondary text-sm">No similar papers found.</p>
                    ) : (
                      <div className="space-y-3">
                        {similar.map((p: any, i: number) => (
                          <SimilarityCard key={i} paper={p} />
                        ))}
                      </div>
                    )}
                  </Tabs.Content>

                  {/* Citations */}
                  <Tabs.Content value="citations">
                    {citations ? (
                      <CitationSummary citations={citations as any} />
                    ) : (
                      <p className="text-text-secondary text-sm">No citation data.</p>
                    )}
                  </Tabs.Content>

                  {/* Suggestions */}
                  <Tabs.Content value="suggestions">
                    {improvements.length === 0 ? (
                      <p className="text-text-secondary text-sm">No suggestions.</p>
                    ) : (
                      <div>
                        {["high", "medium", "low"].map((priority) => {
                          const filtered = improvements.filter(
                            (s: any) => (s.priority || "medium") === priority,
                          );
                          if (filtered.length === 0) return null;
                          return (
                            <div key={priority} className="mb-6">
                              <p className="text-text-secondary uppercase tracking-wide text-xs font-mono mb-3 border-b border-border-subtle pb-1">
                                {priority === "high"
                                  ? "High Priority"
                                  : priority === "medium"
                                    ? "Medium"
                                    : "Low"}
                              </p>
                              {filtered.map((s: any, i: number) => (
                                <SuggestionCard key={i} suggestion={s} />
                              ))}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </Tabs.Content>

                  {/* Journals */}
                  <Tabs.Content value="journals">
                    {journals.length === 0 ? (
                      <p className="text-text-secondary text-sm">No journal matches found.</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {journals.map((j: any, i: number) => (
                          <JournalCard key={i} journal={j} />
                        ))}
                      </div>
                    )}
                  </Tabs.Content>
                </Tabs.Root>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
