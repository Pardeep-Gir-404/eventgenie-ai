import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2, Loader2, Coins, Calendar, CheckSquare, Palette } from 'lucide-react';

const PROGRESS_STAGES = [
  { label: "Grounding event context & local vendor pricing benchmarks...", icon: Sparkles },
  { label: "Synthesizing 100% budget envelope & contingency reserves...", icon: Coins },
  { label: "Backward-planning milestone calendar from event date...", icon: Calendar },
  { label: "Curating negotiation checklists & inquiry messages...", icon: CheckSquare },
  { label: "Architecting bespoke creative concepts & signature moments...", icon: Palette },
  { label: "Executing AI sanity check & finalizing master blueprint...", icon: CheckCircle2 }
];

export default function LoadingSkeleton({ city = "your city", eventType = "event" }) {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < PROGRESS_STAGES.length - 1 ? prev + 1 : prev));
    }, 2200);

    return () => clearInterval(interval);
  }, []);

  const progressPercent = Math.min(100, Math.round(((currentStage + 1) / PROGRESS_STAGES.length) * 100));

  return (
    <div className="w-full max-w-4xl mx-auto py-12 px-4 space-y-8 animate-fadeIn">
      
      {/* Streaming Status Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs sm:text-sm font-semibold shadow-sm">
          <Loader2 className="w-4 h-4 animate-spin text-indigo-600 dark:text-indigo-400" />
          <span>Generative AI Engine At Work</span>
        </div>

        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
          Architecting Your Master Plan
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
          Tailoring a complete, actionable blueprint for your {eventType.replace('_', ' ')} in {city}.
        </p>

        {/* Live Progress Bar */}
        <div className="w-full max-w-md mx-auto mt-4">
          <div className="flex justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">
            <span>Progress</span>
            <span>{progressPercent}%</span>
          </div>
          <div className="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Streaming Steps Checklist */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm max-w-lg mx-auto space-y-3">
        {PROGRESS_STAGES.map((stage, idx) => {
          const Icon = stage.icon;
          const isDone = idx < currentStage;
          const isCurrent = idx === currentStage;

          return (
            <div
              key={idx}
              className={`flex items-center gap-3 text-xs sm:text-sm transition-all duration-300 ${
                isDone
                  ? "text-emerald-600 dark:text-emerald-400 font-medium"
                  : isCurrent
                  ? "text-indigo-600 dark:text-indigo-400 font-bold scale-[1.02]"
                  : "text-slate-400 dark:text-slate-600 opacity-60"
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 animate-spin text-indigo-500 flex-shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-300 dark:border-slate-700 flex-shrink-0"></div>
              )}
              <span className="line-clamp-1">{stage.label}</span>
            </div>
          );
        })}
      </div>

      {/* Skeletons Preview Silhouette */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4 animate-pulse">
          <div className="w-1/2 h-5 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div className="w-32 h-32 mx-auto rounded-full border-8 border-slate-200 dark:border-slate-800"></div>
          <div className="space-y-2 pt-2">
            <div className="w-full h-3 bg-slate-200 dark:bg-slate-800 rounded"></div>
            <div className="w-3/4 h-3 bg-slate-200 dark:bg-slate-800 rounded"></div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4 animate-pulse">
          <div className="w-1/2 h-5 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div className="space-y-3 pt-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-200 dark:bg-slate-800 flex-shrink-0"></div>
                <div className="flex-1 space-y-1.5">
                  <div className="w-full h-3 bg-slate-200 dark:bg-slate-800 rounded"></div>
                  <div className="w-2/3 h-2.5 bg-slate-200 dark:bg-slate-800 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4 animate-pulse">
          <div className="w-1/2 h-5 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div className="h-28 rounded-xl bg-slate-200 dark:bg-slate-800"></div>
          <div className="space-y-2 pt-2">
            <div className="w-full h-3 bg-slate-200 dark:bg-slate-800 rounded"></div>
            <div className="w-1/2 h-3 bg-slate-200 dark:bg-slate-800 rounded"></div>
          </div>
        </div>
      </div>

    </div>
  );
}
