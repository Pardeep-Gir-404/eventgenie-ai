import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Sparkles,
  PieChart,
  Calendar,
  CheckSquare,
  Palette,
  MessageSquare,
  Share2,
  ArrowLeft,
  DollarSign,
  Users,
  MapPin,
  Clock,
  Printer
} from 'lucide-react';

import Navbar from './components/Navbar';
import DemoSelector from './components/DemoSelector';
import WizardForm from './components/WizardForm';
import LoadingSkeleton from './components/LoadingSkeleton';
import ReasoningCard from './components/ReasoningCard';
import BudgetOverview from './components/BudgetOverview';
import TimelineView from './components/TimelineView';
import VendorChecklist from './components/VendorChecklist';
import CreativeIdeas from './components/CreativeIdeas';
import PlanRefinerChat from './components/PlanRefinerChat';
import ExportShareModal from './components/ExportShareModal';
import SavedPlansDrawer from './components/SavedPlansDrawer';

import { api } from './services/api';
import { formatCurrency, getCurrencySymbol } from './utils/currency';

const INITIAL_FORM = {
  event_type: "wedding",
  title: "",
  city: "Jaipur",
  date: "2026-11-20",
  guest_count: 150,
  total_budget: 1200000,
  currency: "INR",
  theme: "Regal Rajasthani Heritage with Candlelight & Marigolds",
  food_preference: "veg",
  setting: "hybrid",
  cultural_preferences: "Traditional Rajasthani Pheras, Sangeet & Folk Fusion",
  special_requests: "Drone photography, live folk musicians, zero single-use plastics"
};

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [activePlan, setActivePlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refining, setRefining] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState(null);
  
  const [activeTab, setActiveTab] = useState("budget"); // budget | timeline | vendors | creative | refiner
  const [demos, setDemos] = useState([]);
  const [savedPlans, setSavedPlans] = useState([]);
  const [health, setHealth] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  const [isSavedDrawerOpen, setIsSavedDrawerOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Sync Dark Mode class
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Initial Load: Health, Demos, Saved Plans, URL planId check
  useEffect(() => {
    async function init() {
      try {
        const [h, d, p] = await Promise.allSettled([
          api.getHealth(),
          api.getDemoScenarios(),
          api.listPlans()
        ]);
        if (h.status === 'fulfilled') setHealth(h.value);
        if (d.status === 'fulfilled') setDemos(d.value);
        if (p.status === 'fulfilled') setSavedPlans(p.value);

        // Check if shared planId in URL
        const params = new URLSearchParams(window.location.search);
        const planId = params.get('planId');
        if (planId) {
          loadPlanById(planId);
        }
      } catch (e) {
        console.error("Initialization error:", e);
      }
    }
    init();
  }, []);

  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    } catch (e) {
      // non-critical
    }
  };

  // Generate Plan Handler
  const handleGeneratePlan = async (dataToSubmit) => {
    setLoading(true);
    try {
      const plan = await api.generatePlan(dataToSubmit);
      setActivePlan(plan);
      setActiveTab("budget");
      triggerConfetti();
      // Refresh saved plans
      api.listPlans().then(setSavedPlans).catch(() => {});
    } catch (err) {
      alert(`Plan Generation Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load Saved Plan
  const loadPlanById = async (planId) => {
    setLoading(true);
    try {
      const plan = await api.getPlan(planId);
      setActivePlan(plan);
      setFormData(plan.request);
      setActiveTab("budget");
    } catch (err) {
      alert(`Could not load plan: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Delete Saved Plan
  const handleDeletePlan = async (planId) => {
    try {
      await api.deletePlan(planId);
      setSavedPlans(prev => prev.filter(p => p.id !== planId));
      if (activePlan?.id === planId) {
        setActivePlan(null);
      }
    } catch (err) {
      alert(`Delete Error: ${err.message}`);
    }
  };

  // Conversational Refinement
  const handleRefinePlan = async (instruction) => {
    if (!activePlan) return;
    setRefining(true);

    const userMsg = {
      role: 'user',
      text: instruction,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatHistory(prev => [...prev, userMsg]);

    try {
      const res = await api.refinePlan(instruction, activePlan);
      setActivePlan(res.updated_plan);

      const aiMsg = {
        role: 'assistant',
        text: res.change_summary,
        version: res.updated_plan.version,
        modified_fields: res.modified_fields,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChatHistory(prev => [...prev, aiMsg]);
      triggerConfetti();
      api.listPlans().then(setSavedPlans).catch(() => {});
    } catch (err) {
      alert(`Refinement Error: ${err.message}`);
    } finally {
      setRefining(false);
    }
  };

  // Regenerate Single Creative Section
  const handleRegenerateSection = async (sectionName) => {
    if (!activePlan) return;
    setRegenerateSectionLocal(sectionName);
    try {
      const res = await api.regenerateSection(sectionName, activePlan);
      const updatedIdeas = { ...activePlan.creative_ideas, [sectionName]: res.new_content };
      const updatedPlan = { ...activePlan, creative_ideas: updatedIdeas };
      setActivePlan(updatedPlan);
      await api.savePlan(updatedPlan);
    } catch (err) {
      alert(`Regeneration Error: ${err.message}`);
    } finally {
      setRegenerateSectionLocal(null);
    }
  };

  const setRegenerateSectionLocal = (name) => {
    setRegeneratingSection(name);
  };

  // Toggle Timeline Task
  const handleToggleTask = async (taskId, newStatus) => {
    if (!activePlan) return;
    try {
      const updatedPlan = await api.toggleTask(taskId, newStatus);
      setActivePlan(updatedPlan);
    } catch (err) {
      // optimistic update locally
      const updatedTasks = activePlan.timeline.tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t);
      const doneCount = updatedTasks.filter(t => t.status === "Done").length;
      const completion_percentage = Math.round((doneCount / updatedTasks.length) * 100);
      setActivePlan({
        ...activePlan,
        timeline: {
          ...activePlan.timeline,
          tasks: updatedTasks,
          completion_percentage
        }
      });
    }
  };

  // Toggle Vendor Checklist Item
  const handleToggleChecklist = async (category, itemText, isCompleted) => {
    if (!activePlan) return;
    // optimistic update
    const updatedChecklists = activePlan.vendor_checklists.map(c => {
      if (c.category.toLowerCase() === category.toLowerCase()) {
        const completed = c.completed_checks ? [...c.completed_checks] : [];
        if (isCompleted && !completed.includes(itemText)) completed.push(itemText);
        if (!isCompleted && completed.includes(itemText)) {
          const idx = completed.indexOf(itemText);
          if (idx > -1) completed.splice(idx, 1);
        }
        return { ...c, completed_checks: completed };
      }
      return c;
    });

    const updatedPlan = { ...activePlan, vendor_checklists: updatedChecklists };
    setActivePlan(updatedPlan);
    try {
      await api.toggleChecklist(category, itemText, isCompleted);
    } catch (e) {
      // silent
    }
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors">
      
      {/* Top Navigation */}
      <Navbar
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        onOpenSavedPlans={() => setIsSavedDrawerOpen(true)}
        onNewPlan={() => {
          setActivePlan(null);
          window.history.pushState({}, document.title, window.location.pathname);
        }}
        savedPlansCount={savedPlans.length}
        health={health}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {loading ? (
          <LoadingSkeleton
            city={formData.city || "your chosen destination"}
            eventType={formData.event_type || "event"}
          />
        ) : !activePlan ? (
          
          /* VIEW 1: HERO & WIZARD FORM */
          <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
            
            {/* Hero Banner */}
            <div className="text-center space-y-3 pt-4 sm:pt-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gradient-to-r from-indigo-50 to-pink-50 dark:from-indigo-950/70 dark:to-pink-950/70 border border-indigo-200/60 dark:border-indigo-800/60 text-indigo-700 dark:text-indigo-300 text-xs sm:text-sm font-bold shadow-sm">
                <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                <span>Next-Gen Autonomous Event Architecture</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                Turn Your Event Dreams into a <span className="gradient-text">Master Plan</span>
              </h1>
              <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
                Powered by Gemini GenAI with <strong>strict deterministic code arithmetic</strong>, backward-planned timelines, and vendor negotiation blueprints.
              </p>
            </div>

            {/* Quick One-Click Demo Scenarios */}
            <DemoSelector
              demos={demos}
              onSelectDemo={(scenarioData) => {
                setFormData(scenarioData);
                handleGeneratePlan(scenarioData);
              }}
              loading={loading}
            />

            {/* Interactive Step Wizard */}
            <WizardForm
              formData={formData}
              setFormData={setFormData}
              onSubmit={handleGeneratePlan}
              loading={loading}
            />

          </div>

        ) : (

          /* VIEW 2: MASTER BLUEPRINT DASHBOARD */
          <div className="space-y-6 animate-fadeIn">
            
            {/* Top Blueprint Summary Bar */}
            <div className="glass-panel p-5 sm:p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
              
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActivePlan(null)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" /> Back to Wizard
                  </button>
                  <span className="text-slate-300 dark:text-slate-700">•</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold uppercase tracking-wider">
                    {activePlan.request.event_type.replace('_', ' ')} (v{activePlan.version})
                  </span>
                </div>

                <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  {activePlan.request.title || `${activePlan.request.event_type.replace('_', ' ')} Blueprint`}
                </h1>

                <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs text-slate-500 dark:text-slate-400 font-medium">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-indigo-500" />
                    {activePlan.request.city}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-purple-500" />
                    {activePlan.request.date}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Users className="w-3.5 h-3.5 text-pink-500" />
                    {activePlan.request.guest_count} Guests
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1 font-bold text-slate-900 dark:text-white">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
                    {formatCurrency(activePlan.budget.total_budget, activePlan.budget.currency)}
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2.5 flex-shrink-0">
                <button
                  onClick={() => setIsExportModalOpen(true)}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 text-slate-800 dark:text-slate-200 shadow-sm transition active:scale-95"
                >
                  <Share2 className="w-4 h-4 text-indigo-500" />
                  <span>Export & Share</span>
                </button>

                <button
                  onClick={() => setActiveTab("refiner")}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md shadow-indigo-500/20 transition active:scale-95"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Refine Plan</span>
                </button>
              </div>

            </div>

            {/* AI Reasoning Card */}
            <ReasoningCard reasoning={activePlan.ai_reasoning} />

            {/* Feature Tabs Navigation */}
            <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 overflow-x-auto scrollbar-none pb-1">
              {[
                { id: "budget", label: "Smart Budget", icon: PieChart },
                { id: "timeline", label: "Automated Timeline", icon: Calendar, badge: `${activePlan.timeline.completion_percentage}%` },
                { id: "vendors", label: "Vendor Checklists", icon: CheckSquare, badge: `${activePlan.vendor_checklists.length} Categories` },
                { id: "creative", label: "Creative Ideas", icon: Palette },
                { id: "refiner", label: "AI Refiner Chat", icon: MessageSquare, badge: "Interactive" }
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                      isActive
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/25"
                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                    {tab.badge && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                        isActive
                          ? "bg-indigo-700 text-indigo-100"
                          : "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                      }`}>
                        {tab.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Tab Views */}
            <div className="pt-2">
              {activeTab === "budget" && (
                <BudgetOverview budget={activePlan.budget} />
              )}

              {activeTab === "timeline" && (
                <TimelineView
                  timeline={activePlan.timeline}
                  onToggleTask={handleToggleTask}
                />
              )}

              {activeTab === "vendors" && (
                <VendorChecklist
                  checklists={activePlan.vendor_checklists}
                  onToggleChecklist={handleToggleChecklist}
                />
              )}

              {activeTab === "creative" && (
                <CreativeIdeas
                  ideas={activePlan.creative_ideas}
                  onRegenerateSection={handleRegenerateSection}
                  regeneratingSection={regeneratingSection}
                />
              )}

              {activeTab === "refiner" && (
                <PlanRefinerChat
                  onRefinePlan={handleRefinePlan}
                  refining={refining}
                  chatHistory={chatHistory}
                />
              )}
            </div>

          </div>

        )}

      </main>

      {/* Export & Share Modal */}
      <ExportShareModal
        plan={activePlan}
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />

      {/* Saved Plans Slide-over Drawer */}
      <SavedPlansDrawer
        isOpen={isSavedDrawerOpen}
        onClose={() => setIsSavedDrawerOpen(false)}
        plans={savedPlans}
        onLoadPlan={loadPlanById}
        onDeletePlan={handleDeletePlan}
      />

      {/* Footer */}
      <footer className="w-full border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 EventGenie AI — Built for Google Cloud & Gemini GenAI Hackathon</p>
          <p className="flex items-center gap-1 text-[11px]">
            <span>FastAPI Backend</span> • <span>React 19 + Tailwind v4</span> • <span>Firestore Database</span>
          </p>
        </div>
      </footer>

    </div>
  );
}
