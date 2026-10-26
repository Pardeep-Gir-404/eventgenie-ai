import React, { useState } from 'react';
import { Calendar, Users, DollarSign, MapPin, Sparkles, AlertCircle, Heart, Palette, UtensilsCrossed, Building2 } from 'lucide-react';
import { getCurrencySymbol } from '../utils/currency';

const EVENT_TYPES = [
  { id: "wedding", label: "Wedding / Sangeet", icon: "💍" },
  { id: "birthday", label: "Birthday Party", icon: "🎂" },
  { id: "college_fest", label: "College / Campus Fest", icon: "🎓" },
  { id: "community_celebration", label: "Community Celebration", icon: "🎉" },
  { id: "corporate", label: "Corporate Gala / Meetup", icon: "💼" },
  { id: "anniversary", label: "Anniversary / Milestone", icon: "🥂" },
  { id: "other", label: "Other Celebration", icon: "✨" }
];

const CURRENCIES = ["INR", "USD", "EUR", "GBP", "AED", "CAD", "AUD", "SGD"];

const FOOD_PREFERENCES = [
  { id: "veg", label: "Pure Vegetarian" },
  { id: "mixed", label: "Veg & Non-Veg Mixed" },
  { id: "non_veg", label: "Non-Veg Primary" },
  { id: "jain", label: "Jain Vegetarian (Strict)" }
];

const SETTINGS = [
  { id: "indoor", label: "Indoor Banquet / Hall" },
  { id: "outdoor", label: "Outdoor Lawn / Open Air" },
  { id: "hybrid", label: "Hybrid (Indoor + Lawn)" }
];

export default function WizardForm({ formData, setFormData, onSubmit, loading }) {
  const [activeStep, setActiveStep] = useState(1);
  const [errorMsg, setErrorMsg] = useState("");

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrorMsg("");
  };

  const validateCurrentStep = () => {
    if (activeStep === 1) {
      if (!formData.city || formData.city.trim().length < 2) {
        setErrorMsg("Please specify the city or location for your event.");
        return false;
      }
      if (!formData.date) {
        setErrorMsg("Please select an event date.");
        return false;
      }
      const selected = new Date(formData.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selected < today) {
        setErrorMsg("Event date cannot be in the past.");
        return false;
      }
    }
    if (activeStep === 2) {
      if (!formData.guest_count || formData.guest_count < 1) {
        setErrorMsg("Please enter a valid guest count (at least 1 attendee).");
        return false;
      }
      if (!formData.total_budget || formData.total_budget <= 0) {
        setErrorMsg("Please enter a realistic total budget.");
        return false;
      }
    }
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setActiveStep(prev => Math.min(3, prev + 1));
    }
  };

  const handlePrev = () => {
    setErrorMsg("");
    setActiveStep(prev => Math.max(1, prev - 1));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateCurrentStep()) {
      onSubmit(formData);
    }
  };

  // Get tomorrow's date as min
  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div className="w-full glass-panel rounded-3xl p-6 sm:p-8 shadow-xl shadow-indigo-500/5 border border-slate-200 dark:border-slate-800">
      
      {/* Step Indicator */}
      <div className="flex items-center justify-between mb-8 pb-5 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2 sm:gap-4 w-full">
          {[
            { step: 1, title: "1. Basics & Date" },
            { step: 2, title: "2. Scale & Budget" },
            { step: 3, title: "3. Theme & Vibe" }
          ].map((s) => (
            <button
              key={s.step}
              type="button"
              onClick={() => {
                if (s.step < activeStep || validateCurrentStep()) {
                  setActiveStep(s.step);
                }
              }}
              className={`flex-1 text-left pb-2 border-b-2 transition-all ${
                activeStep === s.step
                  ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 font-bold"
                  : activeStep > s.step
                  ? "border-emerald-500 text-slate-700 dark:text-slate-300 font-medium"
                  : "border-transparent text-slate-400 dark:text-slate-600 font-normal"
              }`}
            >
              <span className="text-xs sm:text-sm block">{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Validation Alert */}
      {errorMsg && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 flex items-center gap-3 text-sm animate-shake">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* STEP 1: Event Type, City, Date, Title */}
        {activeStep === 1 && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                What type of event are you organizing?
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                {EVENT_TYPES.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => handleChange("event_type", type.id)}
                    className={`flex items-center gap-2 p-3 rounded-xl border text-left text-xs sm:text-sm font-medium transition-all ${
                      formData.event_type === type.id
                        ? "bg-indigo-50 dark:bg-indigo-950/70 border-indigo-500 dark:border-indigo-400 text-indigo-700 dark:text-indigo-300 ring-2 ring-indigo-500/20"
                        : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <span className="text-lg">{type.icon}</span>
                    <span className="line-clamp-1">{type.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                  Host City / Location <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                  <input
                    type="text"
                    required
                    placeholder="e.g. Jaipur, Bangalore, Mumbai, New York"
                    value={formData.city || ""}
                    onChange={(e) => handleChange("city", e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">Grounds venue rates, climate, and local vendor markets.</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                  Target Event Date <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Calendar className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                  <input
                    type="date"
                    required
                    min={todayStr}
                    value={formData.date || ""}
                    onChange={(e) => handleChange("date", e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">Calculates backward milestone dates and seasonality.</p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                Event Title / Couple or Host Names <span className="text-slate-400 font-normal text-xs">(Optional)</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Aarav & Meera's Regal Wedding, TechX Global Summit 2026"
                value={formData.title || ""}
                onChange={(e) => handleChange("title", e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>
          </div>
        )}

        {/* STEP 2: Guests, Budget, Currency */}
        {activeStep === 2 && (
          <div className="space-y-6 animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-1">
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                  Guest Count <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <Users className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                  <input
                    type="number"
                    min="1"
                    max="50000"
                    required
                    placeholder="e.g. 150"
                    value={formData.guest_count || ""}
                    onChange={(e) => handleChange("guest_count", parseInt(e.target.value) || 0)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
                  />
                </div>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                  Total Budget & Currency <span className="text-rose-500">*</span>
                </label>
                <div className="flex gap-2">
                  <select
                    value={formData.currency || "INR"}
                    onChange={(e) => handleChange("currency", e.target.value)}
                    className="w-28 px-3 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {CURRENCIES.map(curr => (
                      <option key={curr} value={curr}>{curr}</option>
                    ))}
                  </select>
                  <div className="relative flex-1">
                    <span className="absolute left-3.5 top-2.5 text-slate-400 font-bold text-sm">
                      {getCurrencySymbol(formData.currency)}
                    </span>
                    <input
                      type="number"
                      min="1000"
                      step="500"
                      required
                      placeholder="e.g. 1200000"
                      value={formData.total_budget || ""}
                      onChange={(e) => handleChange("total_budget", parseFloat(e.target.value) || 0)}
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
                    />
                  </div>
                </div>
                {formData.total_budget > 0 && formData.guest_count > 0 && (
                  <p className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold mt-1.5">
                    Estimated budget per guest: {getCurrencySymbol(formData.currency)}
                    {Math.round(formData.total_budget / formData.guest_count).toLocaleString()} / attendee
                  </p>
                )}
              </div>
            </div>

            {/* Food Style & Setting */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5 flex items-center gap-1.5">
                  <UtensilsCrossed className="w-4 h-4 text-indigo-500" />
                  Food Preference
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {FOOD_PREFERENCES.map(food => (
                    <button
                      key={food.id}
                      type="button"
                      onClick={() => handleChange("food_preference", food.id)}
                      className={`px-3 py-2 rounded-xl text-left text-xs sm:text-sm font-medium border transition ${
                        formData.food_preference === food.id
                          ? "bg-indigo-50 dark:bg-indigo-950/70 border-indigo-500 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-500"
                          : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      {food.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5 flex items-center gap-1.5">
                  <Building2 className="w-4 h-4 text-indigo-500" />
                  Setting Preference
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {SETTINGS.map(setting => (
                    <button
                      key={setting.id}
                      type="button"
                      onClick={() => handleChange("setting", setting.id)}
                      className={`px-3 py-2 rounded-xl text-left text-xs sm:text-sm font-medium border transition ${
                        formData.setting === setting.id
                          ? "bg-indigo-50 dark:bg-indigo-950/70 border-indigo-500 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-500"
                          : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      {setting.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Theme, Cultural Preferences, Special Requests */}
        {activeStep === 3 && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5 flex items-center gap-1.5">
                <Palette className="w-4 h-4 text-indigo-500" />
                Theme or Aesthetic Vision <span className="text-slate-400 font-normal text-xs">(Optional)</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Royal Rajasthani Palace, Cyberpunk Neon, Vintage Botanical Garden, Boho Chic"
                value={formData.theme || ""}
                onChange={(e) => handleChange("theme", e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5 flex items-center gap-1.5">
                <Heart className="w-4 h-4 text-pink-500" />
                Cultural & Regional Traditions <span className="text-slate-400 font-normal text-xs">(Optional)</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Traditional Marwari & Punjabi customs, South Indian Brahmin rituals, Christian chapel vows"
                value={formData.cultural_preferences || ""}
                onChange={(e) => handleChange("cultural_preferences", e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1.5">
                Special Requests & Constraints <span className="text-slate-400 font-normal text-xs">(Optional)</span>
              </label>
              <textarea
                rows="3"
                placeholder="e.g. Drone photography required, nut allergy menu, eco-friendly zero-plastic setup, live classical flute artist"
                value={formData.special_requests || ""}
                onChange={(e) => handleChange("special_requests", e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm resize-none"
              />
            </div>
          </div>
        )}

        {/* Wizard Navigation Footer */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
          {activeStep > 1 ? (
            <button
              type="button"
              onClick={handlePrev}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition active:scale-95 disabled:opacity-50"
            >
              Back
            </button>
          ) : (
            <div></div>
          )}

          {activeStep < 3 ? (
            <button
              type="button"
              onClick={handleNext}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md hover:shadow-indigo-500/20 transition active:scale-95"
            >
              Continue to Step {activeStep + 1} →
            </button>
          ) : (
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-8 py-3 rounded-xl text-base font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 transition-all active:scale-95 disabled:opacity-50"
            >
              <Sparkles className="w-5 h-5 animate-spin" />
              <span>{loading ? "Crafting Your Event Blueprint..." : "Generate Master Plan ✨"}</span>
            </button>
          )}
        </div>

      </form>
    </div>
  );
}
