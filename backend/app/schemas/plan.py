from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime

EventType = Literal[
    "wedding",
    "birthday",
    "college_fest",
    "community_celebration",
    "corporate",
    "anniversary",
    "other"
]

FoodPreference = Literal["veg", "non_veg", "mixed", "jain"]
SettingPreference = Literal["indoor", "outdoor", "hybrid"]
PriorityLevel = Literal["High", "Medium", "Low"]
TaskStatus = Literal["Not started", "In progress", "Done"]

class EventRequest(BaseModel):
    event_type: EventType = Field(..., description="Type of event to plan")
    title: Optional[str] = Field(None, max_length=150, description="Optional custom title for the event")
    city: str = Field(..., min_length=2, max_length=100, description="City / Location of the event")
    date: str = Field(..., description="Target event date in YYYY-MM-DD format")
    guest_count: int = Field(..., ge=1, le=50000, description="Number of anticipated guests")
    total_budget: float = Field(..., gt=0, description="Total budget in chosen currency")
    currency: str = Field(default="INR", min_length=2, max_length=5, description="Currency code (e.g., INR, USD, EUR, GBP, AED)")
    theme: Optional[str] = Field(None, max_length=150, description="Event theme or visual vibe")
    food_preference: FoodPreference = Field(default="mixed", description="Food dietary style")
    setting: SettingPreference = Field(default="indoor", description="Venue environment type")
    cultural_preferences: Optional[str] = Field(None, max_length=200, description="Cultural, traditional, or regional details")
    special_requests: Optional[str] = Field(None, max_length=500, description="Special requests, constraints, or VIP requirements")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            parsed = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed < date.today():
                raise ValueError("Event date cannot be in the past")
        except ValueError as e:
            if "Event date cannot" in str(e):
                raise e
            raise ValueError("Date must be formatted as YYYY-MM-DD")
        return v

    @field_validator("city")
    @classmethod
    def sanitize_city(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("City cannot be empty")
        return v_clean

class BudgetItem(BaseModel):
    category: str = Field(..., description="Budget category name")
    percentage: float = Field(..., description="Normalized percentage of total budget (0-100)")
    amount: float = Field(..., description="Exact computed currency amount")
    notes: str = Field(..., description="Specific recommendation and guidance for this category")
    per_guest_amount: float = Field(..., description="Computed cost per guest for this category")

class CostSavingIdea(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Actionable cost-saving tactic")
    description: str = Field(..., description="How to implement this tactic")
    target_category: str = Field(..., description="Category affected")
    estimated_savings_percentage: float = Field(..., description="Percentage of target category saved")
    estimated_savings_amount: float = Field(..., description="Computed savings in plan currency")
    tradeoff: str = Field(..., description="Any tradeoff or consideration")

class BudgetSummary(BaseModel):
    total_budget: float
    currency: str
    guest_count: int
    cost_per_guest: float
    allocated_total: float
    contingency_percentage: float
    contingency_amount: float
    categories: List[BudgetItem]
    cost_saving_ideas: List[CostSavingIdea]

class TimelineTask(BaseModel):
    id: str
    title: str
    description: str
    days_before_event: int = Field(..., description="Days relative to event date: >0 before, 0 on day, <0 after")
    deadline_date: str = Field(..., description="Calculated ISO date (YYYY-MM-DD)")
    phase: str = Field(..., description="E.g., Milestone, Preparation, Final Week, Event Day")
    priority: PriorityLevel = Field(default="Medium")
    owner_suggestion: str = Field(..., description="Suggested role/person responsible")
    status: TaskStatus = Field(default="Not started")

class TimelineSummary(BaseModel):
    is_rush_plan: bool
    days_until_event: int
    tasks: List[TimelineTask]
    completion_percentage: float

class VendorChecklistItem(BaseModel):
    id: str
    category: str
    what_to_ask: List[str]
    what_to_confirm: List[str]
    negotiation_tips: List[str]
    red_flags: List[str]
    draft_inquiry_message: str
    completed_checks: List[str] = Field(default_factory=list)

class CreativeIdeas(BaseModel):
    decor_concept: str
    invitation_wording: str
    entertainment: List[str]
    games_and_activities: List[str]
    return_gifts_favors: List[str]
    curated_menu_highlights: List[str]
    photo_booth_concept: str
    signature_moment: str

class AIReasoning(BaseModel):
    theme_and_cultural_framing: str
    budget_strategy: str
    seasonality_and_weather: str
    guest_experience_focus: str
    risk_mitigation: str

class EventPlan(BaseModel):
    id: str
    created_at: str
    updated_at: str
    request: EventRequest
    ai_reasoning: AIReasoning
    budget: BudgetSummary
    timeline: TimelineSummary
    vendor_checklists: List[VendorChecklistItem]
    creative_ideas: CreativeIdeas
    version: int = 1

# Schemas for LLM Generation (The raw output before code calculations)
class RawCategoryAllocation(BaseModel):
    category: str
    raw_percentage: float = Field(..., description="Suggested allocation percentage (e.g. 35 for 35%)")
    notes: str

class RawCostSavingIdea(BaseModel):
    title: str
    description: str
    target_category: str
    savings_percent_of_category: float = Field(..., ge=1, le=50, description="Approximate % of that category saved")
    tradeoff: str

class RawTimelineTask(BaseModel):
    title: str
    description: str
    days_before_event: int = Field(..., description="Target days before event (e.g. 60, 30, 14, 7, 1, 0)")
    phase: str
    priority: PriorityLevel
    owner_suggestion: str

class RawPlanGeneration(BaseModel):
    ai_reasoning: AIReasoning
    category_allocations: List[RawCategoryAllocation]
    cost_saving_ideas: List[RawCostSavingIdea]
    timeline_tasks: List[RawTimelineTask]
    vendor_checklists: List[VendorChecklistItem]
    creative_ideas: CreativeIdeas
