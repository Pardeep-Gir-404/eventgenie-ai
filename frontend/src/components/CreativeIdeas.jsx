import React, { useState } from 'react';
import { Sparkles, Wand2, RefreshCw, Music, Gift, Camera, Utensils, Gamepad2, Heart, Award } from 'lucide-react';

export default function CreativeIdeas({ ideas, onRegenerateSection, regeneratingSection }) {
  if (!ideas) return null;

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* 1. Signature Moment (Hero Feature Card) */}
      <div className="relative overflow-hidden p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-purple-900 via-indigo-900 to-pink-900 text-white shadow-xl shadow-purple-500/10">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-pink-500/20 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-amber-300 text-xs font-bold border border-white/20">
              <Award className="w-4 h-4" />
              <span>Crescendo Signature Moment</span>
            </div>
            <h3 className="text-xl sm:text-2xl font-extrabold tracking-tight">
              {ideas.signature_moment}
            </h3>
            <p className="text-xs text-purple-200/80">
              The focal spectacle designed to leave guests breathless and anchor lifelong memories.
            </p>
          </div>

          <button
            onClick={() => onRegenerateSection("signature_moment")}
            disabled={regeneratingSection === "signature_moment"}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white text-xs sm:text-sm font-bold border border-white/30 transition active:scale-95 disabled:opacity-50 flex-shrink-0"
          >
            {regeneratingSection === "signature_moment" ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Wand2 className="w-4 h-4 text-amber-300" />
            )}
            <span>Surprise Me</span>
          </button>
        </div>
      </div>

      {/* Grid of Other Creative Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Decor & Ambience Concept */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>Decor & Lighting Architecture</span>
              </div>
              <button
                onClick={() => onRegenerateSection("decor_concept")}
                disabled={regeneratingSection === "decor_concept"}
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "decor_concept" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {ideas.decor_concept}
            </p>
          </div>
        </div>

        {/* Invitation Wording */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-pink-600 dark:text-pink-400 font-bold text-sm">
                <Heart className="w-4 h-4" />
                <span>Invitation Text & Tone</span>
              </div>
              <button
                onClick={() => onRegenerateSection("invitation_wording")}
                disabled={regeneratingSection === "invitation_wording"}
                className="text-xs text-pink-600 dark:text-pink-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "invitation_wording" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 italic leading-relaxed border-l-2 border-pink-400 pl-3">
              "{ideas.invitation_wording}"
            </p>
          </div>
        </div>

        {/* Photo-Booth Concept */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-bold text-sm">
                <Camera className="w-4 h-4" />
                <span>Photo-Booth & Memories Lounge</span>
              </div>
              <button
                onClick={() => onRegenerateSection("photo_booth_concept")}
                disabled={regeneratingSection === "photo_booth_concept"}
                className="text-xs text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "photo_booth_concept" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {ideas.photo_booth_concept}
            </p>
          </div>
        </div>

        {/* Curated Menu Highlights */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm">
                <Utensils className="w-4 h-4" />
                <span>Curated Gourmet Menu Highlights</span>
              </div>
              <button
                onClick={() => onRegenerateSection("menu")}
                disabled={regeneratingSection === "menu"}
                className="text-xs text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "menu" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <ul className="space-y-1.5 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
              {ideas.curated_menu_highlights && ideas.curated_menu_highlights.map((dish, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{dish}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Entertainment & Music */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-bold text-sm">
                <Music className="w-4 h-4" />
                <span>Entertainment & Musical Cues</span>
              </div>
              <button
                onClick={() => onRegenerateSection("entertainment")}
                disabled={regeneratingSection === "entertainment"}
                className="text-xs text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "entertainment" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <ul className="space-y-1.5 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
              {ideas.entertainment && ideas.entertainment.map((item, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-cyan-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Games & Interactive Activities */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                <Gamepad2 className="w-4 h-4" />
                <span>Interactive Games & Activities</span>
              </div>
              <button
                onClick={() => onRegenerateSection("games_and_activities")}
                disabled={regeneratingSection === "games_and_activities"}
                className="text-xs text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "games_and_activities" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <ul className="space-y-1.5 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
              {ideas.games_and_activities && ideas.games_and_activities.map((item, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Return Gifts & Favors */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between space-y-4 md:col-span-2">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm">
                <Gift className="w-4 h-4" />
                <span>Return Favors & Guest Keepsakes</span>
              </div>
              <button
                onClick={() => onRegenerateSection("return_gifts_favors")}
                disabled={regeneratingSection === "return_gifts_favors"}
                className="text-xs text-rose-600 dark:text-rose-400 hover:underline flex items-center gap-1 font-semibold disabled:opacity-50"
              >
                {regeneratingSection === "return_gifts_favors" ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                <span>Surprise Me</span>
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {ideas.return_gifts_favors && ideas.return_gifts_favors.map((item, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
                  <span className="text-rose-500 font-bold mr-1.5">🎁</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
