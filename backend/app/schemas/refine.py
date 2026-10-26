from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.plan import EventPlan, RawCategoryAllocation, RawCostSavingIdea, RawTimelineTask, CreativeIdeas

class RefineRequest(BaseModel):
    user_instruction: str = Field(..., min_length=2, max_length=1000, description="User instruction for refining the plan")
    current_plan: EventPlan = Field(..., description="The complete existing event plan")

class RawPlanPatch(BaseModel):
    change_summary: str = Field(..., description="Clear explanation of changes made in response to user request")
    modified_fields: List[str] = Field(default_factory=list, description="List of high-level sections modified (e.g., 'budget', 'timeline', 'creative_ideas')")
    new_total_budget: Optional[float] = Field(None, description="Updated total budget if user requested budget change")
    new_event_date: Optional[str] = Field(None, description="Updated event date (YYYY-MM-DD) if user asked to move date")
    new_guest_count: Optional[int] = Field(None, description="Updated guest count if user changed headcount")
    new_theme: Optional[str] = Field(None, description="Updated theme if changed")
    new_food_preference: Optional[str] = Field(None, description="Updated food preference if changed")
    updated_category_allocations: Optional[List[RawCategoryAllocation]] = Field(None, description="Re-balanced budget category weights")
    updated_cost_saving_ideas: Optional[List[RawCostSavingIdea]] = Field(None, description="Updated cost saving ideas")
    added_or_modified_timeline_tasks: Optional[List[RawTimelineTask]] = Field(None, description="New or modified timeline tasks")
    updated_creative_ideas: Optional[CreativeIdeas] = Field(None, description="Updated creative ideas if modified")
    updated_reasoning: Optional[str] = Field(None, description="Updated AI strategy reasoning note")

class RefineResponse(BaseModel):
    updated_plan: EventPlan
    change_summary: str
    modified_fields: List[str]

class RegenerateSectionRequest(BaseModel):
    section: str = Field(..., description="Section to regenerate: 'decor', 'invitation', 'entertainment', 'games', 'return_gifts', 'menu', 'photo_booth', 'signature_moment'")
    current_plan: EventPlan

class RegenerateSectionResponse(BaseModel):
    section: str
    new_content: Any
    explanation: str

class ToggleTaskRequest(BaseModel):
    task_id: str
    status: str

class ToggleChecklistRequest(BaseModel):
    vendor_category: str
    item_text: str
    is_completed: bool
