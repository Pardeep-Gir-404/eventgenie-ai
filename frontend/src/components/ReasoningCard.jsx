import React, { useState } from 'react';
import { Lightbulb, ChevronDown, ChevronUp, ShieldCheck, Sun, HeartHandshake, DollarSign, Sparkles } from 'lucide-react';

export default function ReasoningCard({ reasoning }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!reasoning) return null;

  return (
    <div className="w-full bg-gradient-to-r from-purple-900/10 via-indigo-900/10 to-pink-900/10 dark:from-purple-950/40 dark:via-indigo-950/30 dark:to-pink-950/30 rounded-2xl p-5 sm:p-6 border border-purple-200/60 dark:border-purple-800/40 shadow-sm transition-all mb-8">
      
      {/* Header */}
      <div 
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-500/20">
            <Lightbulb className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Why this plan?
              <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/80 text-purple-700 dark:text-purple-300 font-medium">
                AI Strategic Grounding
              </span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Transparent reasoning behind your customized budget, timeline, and cultural selections
            </p>
          </div>
        </div>

        <button 
          className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          aria-label="Toggle AI Reasoning"
        >
          {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {/* Expanded Content Grid */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5 pt-5 border-t border-purple-200/40 dark:border-purple-800/30 text-xs sm:text-sm animate-fadeIn">
          
          {/* Theme & Cultural Framing */}
          <div className="p-3.5 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-purple-100 dark:border-purple-900/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-purple-900 dark:text-purple-300">
              <Sparkles className="w-4 h-4 text-purple-500" />
              <span>Theme & Cultural Framing</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {reasoning.theme_and_cultural_framing}
            </p>
          </div>

          {/* Budget Allocation Strategy */}
          <div className="p-3.5 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-purple-100 dark:border-purple-900/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-indigo-900 dark:text-indigo-300">
              <DollarSign className="w-4 h-4 text-indigo-500" />
              <span>Budget Allocation Strategy</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {reasoning.budget_strategy}
            </p>
          </div>

          {/* Seasonality & Climate */}
          <div className="p-3.5 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-purple-100 dark:border-purple-900/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-amber-900 dark:text-amber-300">
              <Sun className="w-4 h-4 text-amber-500" />
              <span>Seasonality & Climate Grounding</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {reasoning.seasonality_and_weather}
            </p>
          </div>

          {/* Guest Experience & Risk Mitigation */}
          <div className="p-3.5 rounded-xl bg-white/70 dark:bg-slate-900/60 border border-purple-100 dark:border-purple-900/40 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-emerald-900 dark:text-emerald-300">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Guest Experience & Risk Mitigation</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {reasoning.guest_experience_focus} {reasoning.risk_mitigation}
            </p>
          </div>

        </div>
      )}

    </div>
  );
}
