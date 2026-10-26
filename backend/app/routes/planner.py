from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.schemas.plan import EventRequest, EventPlan
from app.schemas.refine import (
    RefineRequest,
    RefineResponse,
    RegenerateSectionRequest,
    RegenerateSectionResponse,
    ToggleTaskRequest,
    ToggleChecklistRequest
)
from app.schemas.common import DEMO_SCENARIOS, DemoScenario
from app.services.guardrail_service import check_event_safety, sanitize_text
from app.services.gemini_service import gemini_service
from app.services.firestore_service import storage_service

router = APIRouter(prefix="/api/plan", tags=["Planner"])

@router.get("/demos", response_model=List[DemoScenario])
def get_demo_scenarios():
    """Returns pre-filled demo scenarios for one-click judging and testing."""
    return DEMO_SCENARIOS

@router.post("/generate", response_model=EventPlan)
def generate_plan(req: EventRequest):
    """
    Validates input against guardrails, runs multi-step generation chain,
    strictly calculates budget and timeline dates in code, and saves plan.
    """
    # 1. Guardrail checks
    is_safe, error_msg = check_event_safety(
        city=req.city,
        theme=req.theme or "",
        special_requests=req.special_requests or "",
        cultural_prefs=req.cultural_preferences or ""
    )
    if not is_safe:
        raise HTTPException(status_code=400, detail=error_msg)

    # 2. Sanitize text fields
    req.city = sanitize_text(req.city, max_chars=100)
    if req.theme:
        req.theme = sanitize_text(req.theme, max_chars=150)
    if req.special_requests:
        req.special_requests = sanitize_text(req.special_requests, max_chars=500)
    if req.cultural_preferences:
        req.cultural_preferences = sanitize_text(req.cultural_preferences, max_chars=300)

    # 3. Generate plan
    plan = gemini_service.generate_full_plan(req)

    # 4. Save to persistent / in-memory store
    storage_service.save_plan(plan)

    return plan

@router.post("/refine", response_model=RefineResponse)
def refine_plan(req: RefineRequest):
    """
    Conversational plan refiner: edits the current plan via structured patch
    and deterministically recomputes all budget figures and timeline milestones.
    """
    req.user_instruction = sanitize_text(req.user_instruction, max_chars=500)
    if not req.user_instruction:
        raise HTTPException(status_code=400, detail="Refinement instruction cannot be empty.")

    refine_res = gemini_service.refine_plan(req)
    
    # Save updated version
    storage_service.save_plan(refine_res.updated_plan)
    return refine_res

@router.post("/regenerate-section", response_model=RegenerateSectionResponse)
def regenerate_section(req: RegenerateSectionRequest):
    """Regenerates a single creative section without touching the rest of the plan."""
    return gemini_service.regenerate_section(req)

@router.post("/toggle-task", response_model=EventPlan)
def toggle_task(req: ToggleTaskRequest):
    """Updates status of a timeline task and recalculates progress bar."""
    # Find active plan from storage or request
    for p_id in storage_service.in_memory_cache:
        plan = storage_service.get_plan(p_id)
        if plan:
            task_found = False
            for t in plan.timeline.tasks:
                if t.id == req.task_id:
                    t.status = req.status # type: ignore
                    task_found = True
                    break
            if task_found:
                done_count = sum(1 for t in plan.timeline.tasks if t.status == "Done")
                plan.timeline.completion_percentage = round((done_count / max(1, len(plan.timeline.tasks))) * 100, 1)
                storage_service.save_plan(plan)
                return plan
                
    raise HTTPException(status_code=404, detail="Task not found in active plans.")

@router.post("/toggle-checklist", response_model=Dict[str, Any])
def toggle_checklist(req: ToggleChecklistRequest):
    """Toggles completion state of a vendor checklist item."""
    for p_id in storage_service.in_memory_cache:
        plan = storage_service.get_plan(p_id)
        if plan:
            for item in plan.vendor_checklists:
                if item.category.lower() == req.vendor_category.lower():
                    if req.is_completed:
                        if req.item_text not in item.completed_checks:
                            item.completed_checks.append(req.item_text)
                    else:
                        if req.item_text in item.completed_checks:
                            item.completed_checks.remove(req.item_text)
                    storage_service.save_plan(plan)
                    return {"status": "success", "completed_checks": item.completed_checks}

    return {"status": "success", "completed_checks": []}
