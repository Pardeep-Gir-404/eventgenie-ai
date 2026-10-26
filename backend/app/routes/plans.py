from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.schemas.plan import EventPlan
from app.services.firestore_service import storage_service

router = APIRouter(prefix="/api/plans", tags=["Plans Storage"])

@router.get("", response_model=List[Dict[str, Any]])
def list_saved_plans():
    """Lists metadata for all saved plans."""
    return storage_service.list_plans()

@router.get("/{plan_id}", response_model=EventPlan)
def get_plan_by_id(plan_id: str):
    """Retrieves full details for a specific plan."""
    plan = storage_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Event plan not found.")
    return plan

@router.post("/{plan_id}/save", response_model=EventPlan)
def update_or_save_plan(plan_id: str, plan: EventPlan):
    """Explicitly saves or overwrites an event plan."""
    if plan.id != plan_id:
        plan.id = plan_id
    return storage_service.save_plan(plan)

@router.delete("/{plan_id}")
def delete_plan(plan_id: str):
    """Deletes a saved plan."""
    success = storage_service.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan could not be deleted or was not found.")
    return {"status": "success", "message": f"Plan {plan_id} deleted."}
