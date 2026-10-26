import React, { useState } from 'react';
import { X, Calendar, FileText, Share2, Copy, Check, ExternalLink, Printer } from 'lucide-react';
import { api } from '../services/api';

export default function ExportShareModal({ plan, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !plan) return null;

  const shareUrl = `${window.location.origin}?planId=${plan.id}`;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenPdf = () => {
    window.open(api.getPdfPrintUrl(plan.id), '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg glass-panel p-6 sm:p-7 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl space-y-6 relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-5 top-5 p-1.5 rounded-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 text-xs font-bold">
            <Share2 className="w-3.5 h-3.5" />
            <span>Export & Share Hub</span>
          </div>
          <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">
            Export Your Master Plan
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Download your calendar schedule, print an executive PDF, or send a read-only link to collaborators.
          </p>
        </div>

        {/* Export Options Grid */}
        <div className="space-y-3">
          
          {/* Calendar .ics Download */}
          <a
            href={api.getCalendarUrl(plan.id)}
            download
            className="flex items-center justify-between p-4 rounded-2xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md transition group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Apple / Google / Outlook Calendar (.ics)
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Adds all {plan.timeline.tasks.length} milestone deadlines directly to your calendar
                </p>
              </div>
            </div>
            <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
          </a>

          {/* Clean Executive PDF View */}
          <button
            onClick={handleOpenPdf}
            className="w-full flex items-center justify-between p-4 rounded-2xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 hover:border-purple-400 dark:hover:border-purple-600 hover:shadow-md transition group text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950 flex items-center justify-center text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                <Printer className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Executive PDF & Print Document
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Clean, paginated master overview for vendors, clients, and partners
                </p>
              </div>
            </div>
            <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-purple-600" />
          </button>

        </div>

        {/* Shareable Link Section */}
        <div className="pt-2 space-y-2 border-t border-slate-200 dark:border-slate-800">
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Shareable Read-Only Link
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={shareUrl}
              className="flex-1 px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 text-xs font-mono select-all focus:outline-none"
            />
            <button
              onClick={handleCopyLink}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition flex items-center gap-1.5 active:scale-95 flex-shrink-0"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? "Copied!" : "Copy Link"}</span>
            </button>
          </div>
          <p className="text-[11px] text-slate-400">
            Anyone with this link can view the budget, timeline, and vendor checklists.
          </p>
        </div>

      </div>
    </div>
  );
}
