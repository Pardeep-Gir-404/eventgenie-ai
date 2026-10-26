import React, { useState } from 'react';
import { PiggyBank, Users, ShieldAlert, Sparkles, TrendingDown, Info, DollarSign } from 'lucide-react';
import { formatCurrency, getCurrencySymbol } from '../utils/currency';

const PALETTE = [
  "#6366f1", // indigo
  "#ec4899", // pink
  "#8b5cf6", // purple
  "#06b6d4", // cyan
  "#10b981", // emerald
  "#f59e0b", // amber
  "#3b82f6", // blue
  "#ef4444", // red
  "#14b8a6", // teal
  "#84cc16", // lime
];

export default function BudgetOverview({ budget }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  if (!budget || !budget.categories) return null;

  const total = budget.total_budget;
  const currency = budget.currency;
  const categories = budget.categories;
  const savings = budget.cost_saving_ideas || [];

  // Donut chart path calculations
  let accumulatedAngle = 0;
  const slices = categories.map((cat, idx) => {
    const angle = (cat.percentage / 100) * 360;
    const startAngle = accumulatedAngle;
    const endAngle = accumulatedAngle + angle;
    accumulatedAngle += angle;

    const startRad = (startAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);

    const r = 80;
    const cx = 100;
    const cy = 100;

    const x1 = cx + r * Math.cos(startRad);
    const y1 = cy + r * Math.sin(startRad);
    const x2 = cx + r * Math.cos(endRad);
    const y2 = cy + r * Math.sin(endRad);

    const largeArc = angle > 180 ? 1 : 0;
    const pathData = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    return {
      cat,
      color: PALETTE[idx % PALETTE.length],
      pathData,
      idx
    };
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* 4 Summary Metric KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Budget */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <DollarSign className="w-4 h-4 text-indigo-500" />
            <span>Total Budget</span>
          </div>
          <p className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            {formatCurrency(total, currency)}
          </p>
          <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium mt-1">
            Strict 100% allocation balance
          </p>
        </div>

        {/* Cost Per Guest */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Users className="w-4 h-4 text-purple-500" />
            <span>Per Guest Cost</span>
          </div>
          <p className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            {formatCurrency(budget.cost_per_guest, currency)}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
            Across {budget.guest_count} confirmed guests
          </p>
        </div>

        {/* Contingency Buffer */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            <span>Contingency Buffer</span>
          </div>
          <p className="text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400">
            {budget.contingency_percentage}%
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
            {formatCurrency(budget.contingency_amount, currency)} reserve
          </p>
        </div>

        {/* Potential Cost Savings */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <TrendingDown className="w-4 h-4 text-emerald-500" />
            <span>Optimizable Savings</span>
          </div>
          <p className="text-xl sm:text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
            {formatCurrency(savings.reduce((acc, s) => acc + s.estimated_savings_amount, 0), currency)}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
            {savings.length} actionable tactics identified
          </p>
        </div>

      </div>

      {/* Main Visual: Donut Chart & Category Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Interactive SVG Donut Chart (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 text-center flex flex-col items-center">
          <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">
            Allocation Distribution
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-6">
            Hover over arcs to inspect category amounts
          </p>

          <div className="relative w-64 h-64 sm:w-72 sm:h-72 flex items-center justify-center">
            <svg viewBox="0 0 200 200" className="w-full h-full transform -rotate-90">
              {slices.map((slice) => {
                const isHovered = hoveredIdx === slice.idx;
                return (
                  <path
                    key={slice.idx}
                    d={slice.pathData}
                    fill={slice.color}
                    className="cursor-pointer transition-all duration-200 hover:opacity-90"
                    style={{
                      transformOrigin: '100px 100px',
                      transform: isHovered ? 'scale(1.04)' : 'scale(1)'
                    }}
                    onMouseEnter={() => setHoveredIdx(slice.idx)}
                    onMouseLeave={() => setHoveredIdx(null)}
                  />
                );
              })}
              {/* Inner cutout for Donut */}
              <circle cx="100" cy="100" r="50" className="fill-white dark:fill-slate-900" />
            </svg>

            {/* Donut Center Display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center px-4">
              {hoveredIdx !== null ? (
                <>
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider line-clamp-1">
                    {categories[hoveredIdx].category}
                  </span>
                  <span className="text-lg font-extrabold text-slate-900 dark:text-white">
                    {categories[hoveredIdx].percentage}%
                  </span>
                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                    {formatCurrency(categories[hoveredIdx].amount, currency)}
                  </span>
                </>
              ) : (
                <>
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    Total
                  </span>
                  <span className="text-base sm:text-lg font-black text-slate-900 dark:text-white">
                    {formatCurrency(total, currency)}
                  </span>
                  <span className="text-[11px] text-emerald-600 font-semibold">
                    100% Balanced
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Quick Legend Chips */}
          <div className="flex flex-wrap gap-2 justify-center mt-6">
            {categories.map((c, i) => (
              <button
                key={i}
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs transition ${
                  hoveredIdx === i
                    ? "bg-slate-200 dark:bg-slate-700 font-bold scale-105"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                }`}
              >
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PALETTE[i % PALETTE.length] }}></span>
                <span className="line-clamp-1">{c.category}</span>
                <span className="font-semibold text-slate-400">{c.percentage}%</span>
              </button>
            ))}
          </div>

        </div>

        {/* Detailed Breakdown Table (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-x-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Deterministic Breakdown
            </h3>
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-semibold">
              Strict Code Arithmetic
            </span>
          </div>

          <table className="w-full text-left text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 uppercase text-[11px] font-bold">
                <th className="pb-3">Category</th>
                <th className="pb-3 text-center">% Share</th>
                <th className="pb-3 text-right">Amount</th>
                <th className="pb-3 text-right">Per Guest</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {categories.map((cat, idx) => (
                <tr
                  key={idx}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                  className={`transition-colors ${
                    hoveredIdx === idx ? "bg-indigo-50/50 dark:bg-indigo-950/30" : "hover:bg-slate-50 dark:hover:bg-slate-800/40"
                  }`}
                >
                  <td className="py-3 pr-2">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: PALETTE[idx % PALETTE.length] }}></span>
                      <span className="font-semibold text-slate-900 dark:text-white">{cat.category}</span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1 pl-4">
                      {cat.notes}
                    </p>
                  </td>
                  <td className="py-3 px-2 text-center font-bold text-slate-700 dark:text-slate-300">
                    {cat.percentage}%
                  </td>
                  <td className="py-3 px-2 text-right font-extrabold text-slate-900 dark:text-white">
                    {formatCurrency(cat.amount, currency)}
                  </td>
                  <td className="py-3 pl-2 text-right text-slate-500 dark:text-slate-400 font-medium">
                    {formatCurrency(cat.per_guest_amount, currency)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-slate-200 dark:border-slate-700 font-extrabold text-slate-900 dark:text-white">
                <td className="pt-3">Total Allocation</td>
                <td className="pt-3 text-center text-emerald-600">100.0%</td>
                <td className="pt-3 text-right text-indigo-600 dark:text-indigo-400">{formatCurrency(total, currency)}</td>
                <td className="pt-3 text-right">{formatCurrency(budget.cost_per_guest, currency)}</td>
              </tr>
            </tfoot>
          </table>
        </div>

      </div>

      {/* Programmatic Cost Saving Recommendations */}
      {savings.length > 0 && (
        <div className="space-y-4 pt-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <PiggyBank className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Strategic Cost-Saving Tactics
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Calculated programmatically based on your specific venue and catering numbers
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {savings.map((s) => (
              <div
                key={s.id}
                className="p-5 rounded-2xl bg-gradient-to-br from-emerald-50/60 to-teal-50/40 dark:from-emerald-950/30 dark:to-teal-950/20 border border-emerald-200/80 dark:border-emerald-800/40 space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    {s.title}
                  </h4>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300 flex-shrink-0">
                    -{s.estimated_savings_percentage}%
                  </span>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  {s.description}
                </p>

                <div className="pt-2 border-t border-emerald-200/50 dark:border-emerald-800/30 space-y-1">
                  <div className="flex justify-between text-xs font-bold text-emerald-700 dark:text-emerald-300">
                    <span>Est. Savings:</span>
                    <span>{formatCurrency(s.estimated_savings_amount, currency)}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 italic">
                    Tradeoff: {s.tradeoff}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
