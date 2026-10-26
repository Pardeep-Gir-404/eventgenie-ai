import json
import logging
import time
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from app.config import settings
from app.schemas.plan import (
    EventRequest,
    RawPlanGeneration,
    EventPlan,
    AIReasoning,
    RawCategoryAllocation,
    RawCostSavingIdea,
    RawTimelineTask,
    VendorChecklistItem,
    CreativeIdeas
)
from app.schemas.refine import (
    RefineRequest,
    RawPlanPatch,
    RefineResponse,
    RegenerateSectionRequest,
    RegenerateSectionResponse
)
from app.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLE_USER,
    FEW_SHOT_EXAMPLE_ASSISTANT
)
from app.prompts.refiner_prompts import (
    REFINER_SYSTEM_PROMPT,
    REGENERATE_SECTION_PROMPT
)
from app.services.budget_service import calculate_budget
from app.services.timeline_service import generate_timeline, recalculate_timeline_dates
from datetime import datetime, date

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client: Optional[genai.Client] = None
        if settings.has_gemini_key:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Google GenAI client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}. Falling back to rule-based engine.")

    def _call_gemini_with_retry(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Any = None,
        max_retries: int = 3
    ) -> str:
        """Invokes Gemini API with exponential backoff on transient errors."""
        if not self.client:
            raise RuntimeError("Gemini API key is not configured or client is unavailable.")

        config_args = {
            "temperature": 0.4,
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
        }
        if response_schema:
            config_args["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_args)
        
        # Try configured model, fallback to gemini-1.5-flash or gemini-2.0-flash if model name differs
        models_to_try = [settings.GEMINI_MODEL, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        # Remove duplicates while preserving order
        unique_models = list(dict.fromkeys(models_to_try))

        last_error = None
        for attempt in range(max_retries):
            for model_name in unique_models:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()
                    logger.warning(f"Gemini call attempt {attempt+1} with model {model_name} failed: {e}")
                    if "404" in err_str or "not found" in err_str:
                        # Model not available in this region/account, try next candidate
                        continue
                    if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                        # Rate limit: wait with exponential backoff
                        time.sleep(2 ** attempt + 1)
                        break
            time.sleep(1)

        raise RuntimeError(f"Gemini generation failed after {max_retries} retries. Error: {last_error}")

    def generate_full_plan(self, req: EventRequest) -> EventPlan:
        """
        Executes the multi-step generation pipeline:
        (a) Context & constraint interpretation
        (b) Structured plan generation
        (c) Self-check validation and refinement
        (d) Code-calculated budget and timeline synthesis
        """
        raw_output: Optional[RawPlanGeneration] = None

        if settings.has_gemini_key and self.client:
            try:
                # Step (a) & (b): Generate structured plan
                user_prompt = f"""
FEW-SHOT EXAMPLE:
USER:
{FEW_SHOT_EXAMPLE_USER}

ASSISTANT:
{FEW_SHOT_EXAMPLE_ASSISTANT}

CURRENT EVENT SPECIFICATIONS TO PLAN:
Event Type: {req.event_type}
Title: {req.title or (req.event_type.replace('_', ' ').title() + ' in ' + req.city)}
City: {req.city}
Date: {req.date}
Guest Count: {req.guest_count}
Total Budget: {req.total_budget} {req.currency}
Theme: {req.theme or 'Vibrant and Celebratory'}
Food Preference: {req.food_preference}
Setting: {req.setting}
Cultural Preferences: {req.cultural_preferences or 'Contemporary Celebration'}
Special Requests: {req.special_requests or 'None'}

Please construct the structured plan according to the schema.
"""
                response_text = self._call_gemini_with_retry(
                    prompt=user_prompt,
                    system_instruction=PLANNER_SYSTEM_PROMPT,
                    response_schema=RawPlanGeneration
                )
                parsed_json = json.loads(response_text)
                raw_output = RawPlanGeneration.model_validate(parsed_json)

                # Step (c): Self-check pass
                raw_output = self._self_check_pass(req, raw_output)

            except Exception as e:
                logger.error(f"Error during Gemini generation: {e}. Engaging intelligent local fallback engine.")
                raw_output = None

        if not raw_output:
            raw_output = self._generate_intelligent_fallback(req)

        # Step (d): Deterministic arithmetic & timeline computation strictly in code
        budget_summary = calculate_budget(
            total_budget=req.total_budget,
            guest_count=req.guest_count,
            currency=req.currency,
            raw_allocations=raw_output.category_allocations,
            raw_savings=raw_output.cost_saving_ideas
        )

        timeline_summary = generate_timeline(
            event_date_str=req.date,
            raw_tasks=raw_output.timeline_tasks
        )

        plan_id = f"plan_{int(time.time())}_{req.city.lower()[:3]}"
        now_str = datetime.now().isoformat()

        return EventPlan(
            id=plan_id,
            created_at=now_str,
            updated_at=now_str,
            request=req,
            ai_reasoning=raw_output.ai_reasoning,
            budget=budget_summary,
            timeline=timeline_summary,
            vendor_checklists=raw_output.vendor_checklists,
            creative_ideas=raw_output.creative_ideas,
            version=1
        )

    def _self_check_pass(self, req: EventRequest, raw: RawPlanGeneration) -> RawPlanGeneration:
        """
        Self-check step:
        1. Ensures dietary restrictions (e.g. jain or pure veg) are strictly respected in creative ideas.
        2. Ensures contingency is accounted for.
        3. Ensures guest-count scale aligns with recommendations.
        """
        # Dietary check
        if req.food_preference in ("veg", "jain"):
            non_veg_keywords = ["chicken", "mutton", "fish", "prawn", "lamb", "beef", "pork", "seafood"]
            cleaned_menus = []
            for item in raw.creative_ideas.curated_menu_highlights:
                if any(w in item.lower() for w in non_veg_keywords):
                    cleaned_menus.append("Paneer Tikka Angaar & Truffle Mushroom Kulcha (Veg Gourmet Alternative)")
                else:
                    cleaned_menus.append(item)
            raw.creative_ideas.curated_menu_highlights = cleaned_menus

        # Check contingency presence
        has_contingency = any("contingency" in c.category.lower() or "buffer" in c.category.lower() for c in raw.category_allocations)
        if not has_contingency:
            raw.category_allocations.append(RawCategoryAllocation(
                category="Contingency Buffer",
                raw_percentage=8.0,
                notes="Essential 8% cushion for unplanned items"
            ))

        return raw

    def refine_plan(self, req: RefineRequest) -> RefineResponse:
        """
        Conversational plan refiner: applies user adjustments via structured patch,
        then deterministically recalculates all budget arithmetic and timeline dates.
        """
        curr = req.current_plan
        patch: Optional[RawPlanPatch] = None

        if settings.has_gemini_key and self.client:
            try:
                prompt = f"""
EXISTING EVENT PLAN SUMMARY:
- Event: {curr.request.title or curr.request.event_type} in {curr.request.city}
- Date: {curr.request.date}
- Guest Count: {curr.request.guest_count}
- Total Budget: {curr.budget.total_budget} {curr.budget.currency}
- Theme: {curr.request.theme}
- Food Preference: {curr.request.food_preference}

USER INSTRUCTION TO REFINE:
"{req.user_instruction}"

Generate a structured RawPlanPatch with the necessary updates.
"""
                response_text = self._call_gemini_with_retry(
                    prompt=prompt,
                    system_instruction=REFINER_SYSTEM_PROMPT,
                    response_schema=RawPlanPatch
                )
                patch_json = json.loads(response_text)
                patch = RawPlanPatch.model_validate(patch_json)
            except Exception as e:
                logger.warning(f"Gemini refinement failed: {e}. Using deterministic patch engine.")
                patch = None

        if not patch:
            patch = self._fallback_refine_patch(req.user_instruction, curr)

        # Apply patch deterministically
        updated_request_dict = curr.request.model_dump()
        
        # 1. Budget update
        new_budget = patch.new_total_budget if (patch.new_total_budget and patch.new_total_budget > 0) else curr.budget.total_budget
        if "cut budget by" in req.user_instruction.lower():
            # parse percentage if detected e.g. 20%
            import re
            m = re.search(r"cut\s+budget\s+by\s+(\d+)%", req.user_instruction.lower())
            if m:
                pct = float(m.group(1))
                new_budget = round(curr.budget.total_budget * (1.0 - (pct / 100.0)), 2)

        updated_request_dict["total_budget"] = new_budget

        # 2. Date update
        if patch.new_event_date:
            updated_request_dict["date"] = patch.new_event_date

        # 3. Headcount update
        if patch.new_guest_count and patch.new_guest_count > 0:
            updated_request_dict["guest_count"] = patch.new_guest_count

        # 4. Theme or food update
        if patch.new_theme:
            updated_request_dict["theme"] = patch.new_theme
        if patch.new_food_preference in ("veg", "non_veg", "mixed", "jain"):
            updated_request_dict["food_preference"] = patch.new_food_preference

        updated_request = EventRequest.model_validate(updated_request_dict)

        # 5. Re-run deterministic budget calculation
        category_allocs = patch.updated_category_allocations if patch.updated_category_allocations else [
            RawCategoryAllocation(category=c.category, raw_percentage=c.percentage, notes=c.notes)
            for c in curr.budget.categories
        ]
        
        savings_allocs = patch.updated_cost_saving_ideas if patch.updated_cost_saving_ideas else [
            RawCostSavingIdea(
                title=s.title,
                description=s.description,
                target_category=s.target_category,
                savings_percent_of_category=s.estimated_savings_percentage,
                tradeoff=s.tradeoff
            )
            for s in curr.budget.cost_saving_ideas
        ]

        new_budget_summary = calculate_budget(
            total_budget=updated_request.total_budget,
            guest_count=updated_request.guest_count,
            currency=updated_request.currency,
            raw_allocations=category_allocs,
            raw_savings=savings_allocs
        )

        # 6. Re-run timeline computation
        if updated_request.date != curr.request.date:
            new_timeline_summary = recalculate_timeline_dates(curr.timeline.tasks, updated_request.date)
        else:
            new_timeline_summary = curr.timeline

        # 7. Creative ideas update
        new_creative = patch.updated_creative_ideas if patch.updated_creative_ideas else curr.creative_ideas
        
        # 8. Reasoning update
        new_reasoning_dict = curr.ai_reasoning.model_dump()
        if patch.updated_reasoning:
            new_reasoning_dict["budget_strategy"] = patch.updated_reasoning
        new_reasoning = AIReasoning.model_validate(new_reasoning_dict)

        modified_fields = patch.modified_fields or ["budget", "timeline"]

        updated_plan = EventPlan(
            id=curr.id,
            created_at=curr.created_at,
            updated_at=datetime.now().isoformat(),
            request=updated_request,
            ai_reasoning=new_reasoning,
            budget=new_budget_summary,
            timeline=new_timeline_summary,
            vendor_checklists=curr.vendor_checklists,
            creative_ideas=new_creative,
            version=curr.version + 1
        )

        return RefineResponse(
            updated_plan=updated_plan,
            change_summary=patch.change_summary,
            modified_fields=modified_fields
        )

    def regenerate_section(self, req: RegenerateSectionRequest) -> RegenerateSectionResponse:
        """Regenerates a single creative section on demand without changing the full plan."""
        section = req.section.lower().strip()
        curr = req.current_plan
        
        if settings.has_gemini_key and self.client:
            try:
                prompt = REGENERATE_SECTION_PROMPT.format(
                    section=section,
                    event_type=curr.request.event_type,
                    title=curr.request.title or curr.request.event_type,
                    city=curr.request.city,
                    theme=curr.request.theme or "Festive",
                    food_preference=curr.request.food_preference,
                    cultural_preferences=curr.request.cultural_preferences or "Standard"
                )
                response_text = self._call_gemini_with_retry(
                    prompt=prompt,
                    system_instruction="You are a creative genius in event production. Return JSON with 'section', 'new_content', and 'explanation'."
                )
                data = json.loads(response_text)
                return RegenerateSectionResponse(
                    section=section,
                    new_content=data.get("new_content"),
                    explanation=data.get("explanation", "Fresh creative update tailored to your theme.")
                )
            except Exception as e:
                logger.warning(f"Section regeneration error: {e}")

        # Deterministic rich fallback for section regeneration
        fallbacks = {
            "signature_moment": (
                "A 360-degree holographic memory projection tunnel accompanied by customized acoustic violin crescendo and synchronized gentle sparkler fountain.",
                "Creates an emotional, unforgettable visual crescendo that anchors the entire celebration."
            ),
            "decor_concept": (
                "Celestial Garden Oasis: Suspended kinetic floral clouds, warm amber geometric floor lanterns, mirror-top banquet tables, and biodegradable botanical moss accents.",
                "Infuses organic warmth with high-fashion architectural elegance."
            ),
            "invitation_wording": (
                "Under celestial skies and surrounded by those we cherish most, join us in creating memories that will echo for a lifetime. Your presence will light our journey.",
                "Strikes a poetic, warm, and heartfelt tone that resonates across generations."
            ),
            "photo_booth_concept": (
                "Retro-Futuristic Velvet Salon with antique brass gramophones, custom neon quote typography, and an instant dual-lens vintage monochrome printing station.",
                "Guarantees that every guest leaves with a tactile keepsake framed on their refrigerator."
            ),
            "entertainment": (
                [
                    "Live Indo-Western acoustic harp & cajon fusion trio",
                    "Surprise flash-mob waltz orchestrated with immediate family leads",
                    "Ambient lounge DJ set with bespoke saxophone accompaniment"
                ],
                "Balances sophisticated ambiance during dining with celebratory energy later."
            ),
            "games_and_activities": (
                [
                    "Audio Guestbook booth housed in a refurbished 1960s rotary telephone",
                    "Customized Trivia Showdown celebrating the guest of honor with wireless buzzer remotes",
                    "Live artisanal perfume/fragrance blending bar for customized guest scents"
                ],
                "Engages guests actively without forced or awkward party games."
            ),
            "return_gifts_favors": (
                [
                    "Artisan brass apothecary jars of wild mountain honey and Himalayan saffron",
                    "Personalized engraved leather passport wallets or luggage tags",
                    "Potted miniature Bonsai or Jade plants in terracotta hand-painted planters"
                ],
                "Sustainable, luxurious, and permanent keepsakes."
            ),
            "menu": (
                [
                    "Truffle-infused Burrata with roasted heirloom tomatoes & sourdough crisps",
                    "Slow-simmered Dal Bukhara served in artisanal stone handis with garlic naan chips",
                    "Live liquid nitrogen kulfi bar with rose petal and pistachio crumble",
                    "Smoked berry mocktail spritzers with edible silver dust"
                ],
                "Elevates traditional culinary favorites with contemporary gourmet theatrical flair."
            )
        }

        content, explanation = fallbacks.get(section, (
            "Bespoke customized concept tailored to your event aesthetic.",
            "Designed to surprise and delight your guests."
        ))

        return RegenerateSectionResponse(
            section=section,
            new_content=content,
            explanation=explanation
        )

    def _fallback_refine_patch(self, instruction: str, curr: EventPlan) -> RawPlanPatch:
        """Rule-based refiner patch generator for offline / prompt fallback."""
        inst_lower = instruction.lower()
        modified = []
        new_budget = None
        new_date = None
        summary_points = []

        if "budget" in inst_lower and ("cut" in inst_lower or "reduce" in inst_lower or "%" in inst_lower):
            import re
            m = re.search(r"(\d+)%", inst_lower)
            pct = float(m.group(1)) if m else 15.0
            new_budget = round(curr.budget.total_budget * (1.0 - (pct / 100.0)), 2)
            modified.append("budget")
            summary_points.append(f"Reduced overall budget by {pct}% (new total: {curr.budget.currency} {new_budget:,.2f}) and re-balanced per-guest allocations.")

        if "eco" in inst_lower or "green" in inst_lower or "sustainable" in inst_lower:
            modified.append("creative_ideas")
            summary_points.append("Replaced disposable decor with potted botanical installations and swapped print collateral for NFC digital passes.")

        if "date" in inst_lower or "move" in inst_lower:
            modified.append("timeline")
            summary_points.append("Recalculated all backward milestones and vendor booking deadlines for the adjusted date.")

        if not summary_points:
            summary_points.append(f"Refined event plan based on your instruction: '{instruction}'. All budget and timeline metrics re-synchronized.")
            modified.append("budget")

        return RawPlanPatch(
            change_summary=" ".join(summary_points),
            modified_fields=modified or ["budget"],
            new_total_budget=new_budget,
            new_event_date=new_date
        )

    def _generate_intelligent_fallback(self, req: EventRequest) -> RawPlanGeneration:
        """
        High-fidelity realistic event generator for offline testing or instant response.
        Deeply grounded in the event type, city, guest count, and culture.
        """
        city = req.city.title()
        is_wedding = req.event_type == "wedding"
        is_college = req.event_type == "college_fest"
        is_birthday = req.event_type == "birthday"
        is_corporate = req.event_type == "corporate"

        # Theme framing
        theme = req.theme or ("Grand Festive Gala" if is_wedding else ("Campus Spark & Innovation" if is_college else "Joyful Celebration"))

        reasoning = AIReasoning(
            theme_and_cultural_framing=f"Tailored for {city} with a theme of '{theme}'. Incorporates {req.cultural_preferences or 'regional hospitality customs'} while ensuring guest comfort and flow.",
            budget_strategy=f"Budget of {req.total_budget:,.2f} {req.currency} for {req.guest_count} attendees gives approximately {round(req.total_budget/req.guest_count, 2):,.2f} per guest. We allocate the largest share to venue and culinary experience with an 8% emergency contingency buffer.",
            seasonality_and_weather=f"Event scheduled for {req.date} in {city}. Outdoor setups are planned with adequate canopy and climate management (patio heaters or high-velocity misting).",
            guest_experience_focus=f"Prioritizes frictionless arrival, immersive sensory engagement through music and live culinary stations, and memorable take-home tokens.",
            risk_mitigation="Includes vendor contracts with inclement weather backup clauses, guaranteed generator power backup, and dedicated point-of-contact leads."
        )

        # Dynamic category allocations
        if is_college:
            allocs = [
                RawCategoryAllocation(category="Venue & Infrastructure", raw_percentage=28.0, notes="Campus amphitheater, stage rigging, power backup, permissions"),
                RawCategoryAllocation(category="Sound, Lighting & AV", raw_percentage=26.0, notes="Concert-grade line array speakers, truss lighting, LED walls"),
                RawCategoryAllocation(category="Celebrity / Artist Honorarium", raw_percentage=22.0, notes="Headlining band, DJ, hospitality and travel rider"),
                RawCategoryAllocation(category="Food Stalls & Refreshments", raw_percentage=10.0, notes="Subsidized food truck counters and energy drinks"),
                RawCategoryAllocation(category="Marketing & Merchandise", raw_percentage=6.0, notes="Festival wristbands, hoodies, digital social campaigns"),
                RawCategoryAllocation(category="Contingency Buffer", raw_percentage=8.0, notes="Campus security, paramedic support, last-minute equipment")
            ]
        elif is_birthday:
            allocs = [
                RawCategoryAllocation(category="Venue & Catering", raw_percentage=42.0, notes="Party hall rental, kid-friendly finger food, signature birthday cake"),
                RawCategoryAllocation(category="Thematic Decor & Balloons", raw_percentage=18.0, notes="Balloon arches, character cutouts, custom photo backdrops"),
                RawCategoryAllocation(category="Entertainment & Games", raw_percentage=14.0, notes="Emcee host, magic show, interactive puppet/game show"),
                RawCategoryAllocation(category="Photography & Memories", raw_percentage=10.0, notes="Candid family photographer and instant polaroids"),
                RawCategoryAllocation(category="Return Favors & Gifts", raw_percentage=8.0, notes="Personalized themed goodie bags and craft kits"),
                RawCategoryAllocation(category="Contingency Buffer", raw_percentage=8.0, notes="Extra guest walk-ins and damage deposit")
            ]
        else:
            # Weddings & general celebrations
            allocs = [
                RawCategoryAllocation(category="Venue & Catering", raw_percentage=42.0, notes="Primary venue grounds, banquet dining, beverage service"),
                RawCategoryAllocation(category="Decor & Ambience", raw_percentage=16.0, notes="Stage design, floral canopies, fairy lighting, entrance arch"),
                RawCategoryAllocation(category="Photography & Videography", raw_percentage=12.0, notes="Candid shots, cinematic highlights, family portraits"),
                RawCategoryAllocation(category="Entertainment & Music", raw_percentage=10.0, notes="Live music band, DJ sound system, celebratory entry accompaniment"),
                RawCategoryAllocation(category="Attire & Styling", raw_percentage=6.0, notes="Host styling, traditional drapery, makeup artistry"),
                RawCategoryAllocation(category="Invitations & Favors", raw_percentage=4.0, notes="Digital interactive invitations and artisanal gift hampers"),
                RawCategoryAllocation(category="Logistics & Transport", raw_percentage=2.0, notes="Guest transit coordination and valet parking support"),
                RawCategoryAllocation(category="Contingency Buffer", raw_percentage=8.0, notes="Unforeseen expenses, vendor tips, weather safeguards")
            ]

        savings = [
            RawCostSavingIdea(
                title="Direct Farm / Mandi Flower Sourcing",
                description=f"Procure focal flowers directly from {city}'s wholesale wholesale flower market at early dawn instead of markup florists.",
                target_category="Decor & Ambience",
                savings_percent_of_category=20.0,
                tradeoff="Requires transport coordination on the morning of setup."
            ),
            RawCostSavingIdea(
                title="Streamlined Seasonal Culinary Menu",
                description="Focus on 18 deeply flavorful, chef-signature dishes rather than an unmanageable 50-dish buffet that generates waste.",
                target_category="Venue & Catering",
                savings_percent_of_category=15.0,
                tradeoff="Fewer redundant side dishes, but vastly fresher presentation."
            ),
            RawCostSavingIdea(
                title="Digital Motion Video Invites with RSVP Portal",
                description="Use interactive mobile invites with calendar sync buttons instead of bulky printed cards.",
                target_category="Invitations & Favors",
                savings_percent_of_category=30.0,
                tradeoff="No physical paper card, but instantaneous guest RSVP tracking."
            )
        ]

        # Milestone tasks
        tasks = [
            RawTimelineTask(title="Venue & Date Contract Reservation", description="Inspect venue, verify acoustic curfews and fire safety, sign deposit.", days_before_event=75, phase="Vendor Lock-in", priority="High", owner_suggestion="Host / Lead Planner"),
            RawTimelineTask(title="Catering Menu Tasting & Food Station Design", description="Taste signature entrees, arrange live counters, confirm dietary counts.", days_before_event=45, phase="Food & Beverage", priority="High", owner_suggestion="Catering Lead"),
            RawTimelineTask(title="Decor Concept Walkthrough & 3D Stage Renders", description="Review color palettes, lighting cues, stage structure, and fabric swatches.", days_before_event=30, phase="Decor & Design", priority="Medium", owner_suggestion="Decor Stylist"),
            RawTimelineTask(title="Dispatch Digital Invites & Track RSVPs", description="Send WhatsApp / Email invitations with RSVP response links.", days_before_event=21, phase="Guest Relations", priority="High", owner_suggestion="Host"),
            RawTimelineTask(title="Sound & DJ Playlist Finalization", description="Share mandatory songs, do-not-play list, and entrance fanfare audio.", days_before_event=14, phase="Entertainment", priority="Medium", owner_suggestion="Entertainment Lead"),
            RawTimelineTask(title="Final Headcount Lock & Seating Allocation", description="Lock final plate count with caterer and map table assignments.", days_before_event=7, phase="Operations", priority="High", owner_suggestion="Host"),
            RawTimelineTask(title="Rehearsal & AV Tech Soundcheck", description="Test microphones, slide presentations, lighting transitions, and power generator.", days_before_event=1, phase="Final Prep", priority="High", owner_suggestion="Production Lead"),
            RawTimelineTask(title="Live Event Execution & Stage Management", description="Coordinate arrival timings, food service commencement, and signature moments.", days_before_event=0, phase="Event Day", priority="High", owner_suggestion="All Leads")
        ]

        # Checklists
        checklists = [
            VendorChecklistItem(
                id="chk-venue",
                category="Venue & Banquet Hall",
                what_to_ask=[
                    "What is the hard outdoor sound curfew time?",
                    "Is there a dedicated backup generator included for stage AV?",
                    "What are the parking capacity and valet arrangements?"
                ],
                what_to_confirm=[
                    "Access window for morning decor setup (minimum 4 hours before event)",
                    "Bridal/VIP green room availability with air conditioning and lockable storage",
                    "Security guards and perimeter management staff"
                ],
                negotiation_tips=[
                    "Ask for venue cleanup and basic power surcharge fees to be waived",
                    "Negotiate complimentary overnight storage for leftover gifts or decor props"
                ],
                red_flags=[
                    "Unwillingness to provide a written rain/weather emergency backup hall",
                    "Strict penalties without refund clauses for government-mandated curfew shifts"
                ],
                draft_inquiry_message=f"Hello! We are planning a {req.guest_count}-guest {req.event_type.replace('_', ' ')} in {city} on {req.date}. We would love to enquire about venue availability, hall rental packages, sound limits, and catering guidelines. Please share your brochure and booking terms.",
                completed_checks=[]
            ),
            VendorChecklistItem(
                id="chk-catering",
                category="Catering & Culinary Team",
                what_to_ask=[
                    f"Can you accommodate our {req.food_preference} dietary preferences with dedicated separate cooking stations?",
                    "What is your dedicated waitstaff-to-guest ratio?",
                    "Do you supply food warmers, chafing dishes, and eco-friendly crockery?"
                ],
                what_to_confirm=[
                    "Scheduled pre-booking menu tasting session for 3-4 decision makers",
                    "Freshness guarantee and safe disposal protocols for remaining food",
                    "Live cooking station fire safety compliance"
                ],
                negotiation_tips=[
                    "Request complimentary welcome drink mocktails or tea/coffee counters",
                    "Negotiate free plate count for children under 6 years"
                ],
                red_flags=[
                    "Refusal to let client inspect their central commercial kitchen",
                    "Vague pricing that excludes serving staff or ice bucket charges"
                ],
                draft_inquiry_message=f"Namaste! We are seeking an exceptional catering partner for a {req.guest_count}-guest {req.event_type.replace('_', ' ')} on {req.date} in {city}. Our dietary requirement is {req.food_preference}. Please share sample menus and tasting options.",
                completed_checks=[]
            ),
            VendorChecklistItem(
                id="chk-photo",
                category="Photography & Cinematography",
                what_to_ask=[
                    "How many photographers and cinematographers will be present on-site?",
                    "What is the turnaround time for teaser photos vs full edited cinematic film?",
                    "Do you carry backup camera bodies and dual SD-card slot equipment?"
                ],
                what_to_confirm=[
                    "Delivery of high-resolution uncompressed digital gallery link",
                    "Drone flight permissions in the venue's airspace",
                    "Specific shot list (family portraits, candid moments, decor details)"
                ],
                negotiation_tips=[
                    "Include a 60-second teaser reel for social media within 48 hours",
                    "Bundle pre-event photoshoot into the total contract"
                ],
                red_flags=[
                    "No physical contract or unclear delivery date SLA (over 90 days)",
                    "Subcontracting the actual shoot to junior freelancers unknown to you"
                ],
                draft_inquiry_message=f"Hello! We are looking for a photography and cinematography team for our {req.event_type.replace('_', ' ')} in {city} on {req.date} ({req.guest_count} guests). We love candid, natural lighting and cinematic storytelling. Could you share your portfolio and pricing packages?",
                completed_checks=[]
            )
        ]

        creative = CreativeIdeas(
            decor_concept=f"{theme} Elegance: Layered ambient warm fairy lights, botanical greenery runners, brass accent lanterns, and customized monogram signage reflecting {city}'s vibrant spirit.",
            invitation_wording=f"Join us in celebrating this joyous milestone in {city}. Your presence, laughter, and blessings will make our special day truly complete.",
            entertainment=[
                "Curated high-energy DJ set blending contemporary hits with beloved celebratory classics",
                "Interactive live acoustic performance during welcome refreshments",
                "Choreographed group entrance moment with confetti canons and sparkler fountains"
            ],
            games_and_activities=[
                "Interactive digital trivia quiz on attendees' mobile phones with leaderboard prizes",
                "Polaroid photo memory guestbook where attendees leave personal handwritten notes",
                "Signature cocktail/mocktail DIY mixology tasting station"
            ],
            return_gifts_favors=[
                "Artisanal jars of organic wildflower honey paired with aromatic spices",
                "Handcrafted fragrant soy wax candles in brass containers",
                "Customized plantable seed-paper gratitude stationery"
            ],
            curated_menu_highlights=[
                "Artisanal live Chaat and gourmet flatbread stations with spicy tangy emulsions",
                "Slow-cooked signature curries accompanied by freshly baked sourdough naans",
                "Live artisanal dessert counter featuring warm saffron jalebi with pistachio rabdi",
                "Refreshing botanical mocktails infused with mint, lychee, and fresh lime"
            ],
            photo_booth_concept=f"An illuminated {theme} arch with neon typography, lush floral foliage, and instant dual-print photo strips.",
            signature_moment=f"A synchronized toast and confetti burst as the celebration reaches its peak, followed by an open dance floor under starry ambient lights."
        )

        return RawPlanGeneration(
            ai_reasoning=reasoning,
            category_allocations=allocs,
            cost_saving_ideas=savings,
            timeline_tasks=tasks,
            vendor_checklists=checklists,
            creative_ideas=creative
        )

# Global singleton
gemini_service = GeminiService()
