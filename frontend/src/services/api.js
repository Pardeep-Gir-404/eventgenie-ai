/**
 * EventGenie AI API Service Client
 */

const API_BASE = "/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      let errDetail = `Server responded with ${res.status}`;
      try {
        const errorJson = await res.json();
        errDetail = errorJson.detail || errDetail;
      } catch (e) {
        // ignore parse error
      }
      throw new Error(errDetail);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request("/health"),

  // Demo Scenarios
  getDemoScenarios: () => request("/plan/demos"),

  // Master Plan Generation
  generatePlan: (eventData) => request("/plan/generate", {
    method: "POST",
    body: JSON.stringify(eventData)
  }),

  // Conversational Plan Refinement
  refinePlan: (userInstruction, currentPlan) => request("/plan/refine", {
    method: "POST",
    body: JSON.stringify({
      user_instruction: userInstruction,
      current_plan: currentPlan
    })
  }),

  // Regenerate Single Section
  regenerateSection: (section, currentPlan) => request("/plan/regenerate-section", {
    method: "POST",
    body: JSON.stringify({
      section,
      current_plan: currentPlan
    })
  }),

  // Toggle Task Status
  toggleTask: (taskId, status) => request("/plan/toggle-task", {
    method: "POST",
    body: JSON.stringify({ task_id: taskId, status })
  }),

  // Toggle Vendor Checklist Item
  toggleChecklist: (vendorCategory, itemText, isCompleted) => request("/plan/toggle-checklist", {
    method: "POST",
    body: JSON.stringify({
      vendor_category: vendorCategory,
      item_text: itemText,
      is_completed: isCompleted
    })
  }),

  // Plans Management
  listPlans: () => request("/plans"),
  getPlan: (planId) => request(`/plans/${planId}`),
  savePlan: (plan) => request(`/plans/${plan.id}/save`, {
    method: "POST",
    body: JSON.stringify(plan)
  }),
  deletePlan: (planId) => request(`/plans/${planId}`, {
    method: "DELETE"
  }),

  // Exports URLs
  getCalendarUrl: (planId) => `/api/export/${planId}/calendar.ics`,
  getPdfPrintUrl: (planId) => `/api/export/${planId}/pdf`,
  getShareUrl: (planId) => `/api/export/${planId}/share`
};
