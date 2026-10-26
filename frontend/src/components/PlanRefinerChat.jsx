import React, { useState } from 'react';
import { Send, Sparkles, Wand2, CheckCircle2, RefreshCw, MessageSquare, ArrowRight, CornerDownLeft } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  "Cut overall budget by 15%",
  "Make the event zero-waste and eco-friendly",
  "Switch catering to 100% pure Jain vegetarian",
  "Add drone cinematography & live streaming",
  "Move date forward by 10 days"
];

export default function PlanRefinerChat({ onRefinePlan, refining, chatHistory = [] }) {
  const [instruction, setInstruction] = useState("");

  const handleSend = (text) => {
    const query = text || instruction;
    if (!query.trim() || refining) return;
    onRefinePlan(query.trim());
    setInstruction("");
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="glass-panel rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden flex flex-col h-[520px] animate-fadeIn">
      
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-r from-indigo-50/80 via-purple-50/80 to-pink-50/80 dark:from-indigo-950/40 dark:via-purple-950/30 dark:to-pink-950/30 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
              Conversational Plan Refiner
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Instruct the AI to adjust your plan. All numbers recalculate automatically in code.
            </p>
          </div>
        </div>

        <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-semibold hidden sm:inline-block">
          Dynamic Patching Active
        </span>
      </div>

      {/* Suggested Quick Prompt Pills */}
      <div className="p-3 bg-slate-50 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2 overflow-x-auto scrollbar-none">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex-shrink-0 ml-1">
          Suggestions:
        </span>
        {SUGGESTED_PROMPTS.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            disabled={refining}
            className="text-xs px-3 py-1 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 whitespace-nowrap transition-colors flex-shrink-0 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Body */}
      <div className="flex-1 p-4 sm:p-5 overflow-y-auto space-y-4">
        {chatHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-2">
            <MessageSquare className="w-10 h-10 text-indigo-300 dark:text-indigo-700 stroke-1" />
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              No refinements yet
            </h4>
            <p className="text-xs max-w-sm text-slate-500 dark:text-slate-400">
              Type an instruction below (e.g. "Cut catering budget", "Shift date to December", "Make decor more traditional") to iterate conversationally.
            </p>
          </div>
        ) : (
          chatHistory.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-1 animate-fadeIn`}
            >
              <div
                className={`max-w-[85%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-br-none shadow-sm'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none shadow-sm space-y-2'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Plan Refined (v{msg.version || 'Updated'})</span>
                  </div>
                )}

                <p>{msg.text}</p>

                {/* Highlighted Modified Sections Badges */}
                {msg.modified_fields && msg.modified_fields.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-100 dark:border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-400">
                      Recalculated:
                    </span>
                    {msg.modified_fields.map((f, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-semibold uppercase"
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <span className="text-[10px] text-slate-400 px-1">
                {msg.timestamp || 'Just now'}
              </span>
            </div>
          ))
        )}

        {refining && (
          <div className="flex items-center gap-2 p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300 w-fit animate-pulse">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-500" />
            <span>Refining plan, patching structured data & re-calculating math...</span>
          </div>
        )}
      </div>

      {/* Input Form Bar */}
      <div className="p-3 sm:p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Type refinement... (e.g. 'cut budget by 20%', 'more vegan options')"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={refining}
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs sm:text-sm"
          />
          <button
            onClick={() => handleSend()}
            disabled={!instruction.trim() || refining}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition active:scale-95 disabled:opacity-50 flex items-center justify-center"
            title="Send Refinement"
          >
            {refining ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>

    </div>
  );
}
