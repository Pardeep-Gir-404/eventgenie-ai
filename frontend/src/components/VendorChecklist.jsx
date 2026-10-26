import React, { useState } from 'react';
import { CheckSquare, MessageCircle, Mail, Copy, Check, AlertOctagon, HelpCircle, FileCheck, DollarSign } from 'lucide-react';

export default function VendorChecklist({ checklists = [], onToggleChecklist }) {
  const [activeCategoryIdx, setActiveCategoryIdx] = useState(0);
  const [copied, setCopied] = useState(false);

  if (!checklists || checklists.length === 0) return null;

  const current = checklists[activeCategoryIdx] || checklists[0];

  const handleCopyMessage = () => {
    navigator.clipboard.writeText(current.draft_inquiry_message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isChecked = (itemText) => {
    return current.completed_checks && current.completed_checks.includes(itemText);
  };

  const handleToggle = (itemText) => {
    const nextState = !isChecked(itemText);
    onToggleChecklist(current.category, itemText, nextState);
  };

  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(current.draft_inquiry_message)}`;
  const mailtoUrl = `mailto:?subject=${encodeURIComponent(`Inquiry: ${current.category} for Event`)}&body=${encodeURIComponent(current.draft_inquiry_message)}`;

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {checklists.map((cat, idx) => (
          <button
            key={cat.id || idx}
            onClick={() => setActiveCategoryIdx(idx)}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold flex-shrink-0 transition-all ${
              activeCategoryIdx === idx
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
                : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
            }`}
          >
            {cat.category}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left: 4 Checklist Sections (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* 1. What to Ask */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400 font-bold text-sm">
              <HelpCircle className="w-4 h-4" />
              <span>Questions to Ask During Initial Meeting</span>
            </div>
            <div className="space-y-2">
              {current.what_to_ask.map((item, i) => (
                <label
                  key={i}
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition ${
                    isChecked(item)
                      ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800 line-through text-slate-400"
                      : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 hover:border-indigo-300"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked(item)}
                    onChange={() => handleToggle(item)}
                    className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                  />
                  <span className="text-xs sm:text-sm leading-relaxed">{item}</span>
                </label>
              ))}
            </div>
          </div>

          {/* 2. What to Confirm in Contract */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-bold text-sm">
              <FileCheck className="w-4 h-4" />
              <span>Clauses to Confirm in Writing Before Deposit</span>
            </div>
            <div className="space-y-2">
              {current.what_to_confirm.map((item, i) => (
                <label
                  key={i}
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition ${
                    isChecked(item)
                      ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800 line-through text-slate-400"
                      : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 hover:border-emerald-300"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked(item)}
                    onChange={() => handleToggle(item)}
                    className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                  />
                  <span className="text-xs sm:text-sm leading-relaxed">{item}</span>
                </label>
              ))}
            </div>
          </div>

          {/* 3. Negotiation Tips */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50/50 to-orange-50/30 dark:from-amber-950/20 dark:to-orange-950/10 border border-amber-200/80 dark:border-amber-800/40 space-y-3">
            <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-bold text-sm">
              <DollarSign className="w-4 h-4" />
              <span>Negotiation Hacks & Cost Levers</span>
            </div>
            <ul className="space-y-2 text-xs sm:text-sm text-amber-900 dark:text-amber-200">
              {current.negotiation_tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 4. Red Flags */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-rose-50/50 to-red-50/30 dark:from-rose-950/20 dark:to-red-950/10 border border-rose-200/80 dark:border-rose-800/40 space-y-3">
            <div className="flex items-center gap-2 text-rose-800 dark:text-rose-300 font-bold text-sm">
              <AlertOctagon className="w-4 h-4 text-rose-500" />
              <span>Critical Red Flags to Watch Out For</span>
            </div>
            <ul className="space-y-2 text-xs sm:text-sm text-rose-900 dark:text-rose-200">
              {current.red_flags.map((flag, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">⚠️</span>
                  <span>{flag}</span>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Right: Vendor Inquiry Message Generator (4 cols) */}
        <div className="lg:col-span-4 sticky top-24 glass-panel p-5 sm:p-6 rounded-3xl border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <MessageCircle className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                Shortlist Inquiry Generator
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Ready to send via WhatsApp or Email
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
            {current.draft_inquiry_message}
          </div>

          <div className="flex flex-col gap-2 pt-2">
            <button
              onClick={handleCopyMessage}
              className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition active:scale-95"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? "Message Copied!" : "Copy Inquiry Message"}</span>
            </button>

            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition active:scale-95"
            >
              <MessageCircle className="w-4 h-4" />
              <span>Send via WhatsApp</span>
            </a>

            <a
              href={mailtoUrl}
              className="w-full inline-flex items-center justify-center gap-2 py-2 px-4 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition"
            >
              <Mail className="w-3.5 h-3.5 text-slate-400" />
              <span>Send via Email Client</span>
            </a>
          </div>
        </div>

      </div>

    </div>
  );
}
