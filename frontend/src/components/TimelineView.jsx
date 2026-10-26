import React, { useState } from 'react';
import { Calendar, CheckCircle2, Clock, AlertTriangle, UserCheck, Flame, Filter, Zap } from 'lucide-react';

const PRIORITY_COLORS = {
  High: "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border-rose-200 dark:border-rose-900",
  Medium: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border-amber-200 dark:border-amber-900",
  Low: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-900"
};

const STATUS_OPTIONS = ["Not started", "In progress", "Done"];

export default function TimelineView({ timeline, onToggleTask }) {
  const [filter, setFilter] = useState("all");

  if (!timeline || !timeline.tasks) return null;

  const tasks = timeline.tasks;
  const isRush = timeline.is_rush_plan;
  const daysUntil = timeline.days_until_event;
  const progressPct = timeline.completion_percentage;

  const filteredTasks = tasks.filter(t => {
    if (filter === "all") return true;
    return t.status.toLowerCase() === filter.toLowerCase();
  });

  const handleStatusCycle = (task) => {
    const currentIndex = STATUS_OPTIONS.indexOf(task.status);
    const nextStatus = STATUS_OPTIONS[(currentIndex + 1) % STATUS_OPTIONS.length];
    onToggleTask(task.id, nextStatus);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Rush Plan Banner */}
      {isRush && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-rose-500/10 to-orange-500/10 border border-amber-300 dark:border-amber-700/60 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center flex-shrink-0 animate-bounce">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-amber-900 dark:text-amber-200 flex items-center gap-2">
              Compressed Rush Plan Activated
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-200 dark:bg-amber-900 text-amber-800 dark:text-amber-200 font-bold">
                {daysUntil} Days Notice
              </span>
            </h4>
            <p className="text-xs text-amber-800/80 dark:text-amber-300/80 mt-0.5">
              Your event date is in under 7 days. Critical milestones have been compressed into an urgent hourly turnaround sequence.
            </p>
          </div>
        </div>
      )}

      {/* Progress & Live Countdown Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Backward-Planned Milestones
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Real calendar deadlines calculated strictly backwards from your event day
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-xs font-bold border border-indigo-200 dark:border-indigo-800">
              {daysUntil >= 0 ? `T-${daysUntil} Days Remaining` : `Event Concluded`}
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 text-xs font-bold border border-emerald-200 dark:border-emerald-800">
              {tasks.filter(t => t.status === "Done").length} of {tasks.length} Completed
            </div>
          </div>
        </div>

        {/* Live Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold text-slate-600 dark:text-slate-300">
            <span>Overall Execution Progress</span>
            <span className="font-extrabold text-indigo-600 dark:text-indigo-400">{progressPct}%</span>
          </div>
          <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden p-0.5">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            ></div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </span>
          {["all", "Not started", "In progress", "Done"].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                filter.toLowerCase() === status.toLowerCase()
                  ? "bg-indigo-600 text-white font-bold"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {status === "all" ? "All Tasks" : status}
            </button>
          ))}
        </div>
      </div>

      {/* Tasks Chronological Feed */}
      <div className="space-y-3">
        {filteredTasks.map((task) => {
          const isDone = task.status === "Done";
          const isInProgress = task.status === "In progress";

          return (
            <div
              key={task.id}
              className={`glass-panel p-4 sm:p-5 rounded-2xl border transition-all duration-200 ${
                isDone
                  ? "border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/20 dark:bg-emerald-950/10 opacity-80"
                  : isInProgress
                  ? "border-indigo-300 dark:border-indigo-800 shadow-sm"
                  : "border-slate-200 dark:border-slate-800"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                
                {/* Left: Checkbox / Status + Title + Date */}
                <div className="flex items-start gap-3 flex-1">
                  
                  {/* Status Toggle Button */}
                  <button
                    onClick={() => handleStatusCycle(task)}
                    className="mt-0.5 flex-shrink-0 transition-transform active:scale-90"
                    title="Click to cycle status"
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 fill-emerald-100 dark:fill-emerald-950" />
                    ) : isInProgress ? (
                      <Clock className="w-5 h-5 text-indigo-500 animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-slate-300 dark:border-slate-600 hover:border-indigo-500"></div>
                    )}
                  </button>

                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold">
                        {task.phase}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-bold ${PRIORITY_COLORS[task.priority] || PRIORITY_COLORS.Medium}`}>
                        {task.priority} Priority
                      </span>
                      <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                        • {task.deadline_date}
                      </span>
                    </div>

                    <h4 className={`text-sm sm:text-base font-bold ${isDone ? "line-through text-slate-500 dark:text-slate-400" : "text-slate-900 dark:text-white"}`}>
                      {task.title}
                    </h4>

                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {task.description}
                    </p>
                  </div>
                </div>

                {/* Right: Owner & Status Badge */}
                <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-2 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-slate-800">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
                    <UserCheck className="w-3.5 h-3.5 text-indigo-500" />
                    <span>{task.owner_suggestion}</span>
                  </div>

                  <button
                    onClick={() => handleStatusCycle(task)}
                    className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition ${
                      isDone
                        ? "bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200"
                        : isInProgress
                        ? "bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    {task.status}
                  </button>
                </div>

              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
