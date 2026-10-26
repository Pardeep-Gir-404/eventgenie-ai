import React from 'react';
import { Sparkles, PartyPopper, Rocket, Zap } from 'lucide-react';

const ICON_MAP = {
  sparkles: Sparkles,
  "party-popper": PartyPopper,
  rocket: Rocket
};

export default function DemoSelector({ demos = [], onSelectDemo, loading }) {
  if (!demos || demos.length === 0) return null;

  return (
    <div className="w-full bg-gradient-to-r from-indigo-50/70 via-purple-50/70 to-pink-50/70 dark:from-indigo-950/40 dark:via-purple-950/30 dark:to-pink-950/30 rounded-2xl p-4 sm:p-5 border border-indigo-100/80 dark:border-indigo-900/40 shadow-sm mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500 fill-amber-500" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300">
            One-Click Judge & Demo Scenarios
          </h2>
        </div>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          Click any scenario to populate the form instantly
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {demos.map((d) => {
          const IconComp = ICON_MAP[d.icon] || Sparkles;
          return (
            <button
              key={d.id}
              onClick={() => onSelectDemo(d.data)}
              disabled={loading}
              className="group text-left p-3.5 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md transition-all active:scale-[0.98] disabled:opacity-50"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                  <IconComp className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {d.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">
                    {d.subtitle}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
