import math
from typing import List, Dict, Tuple
from app.schemas.plan import BudgetItem, CostSavingIdea, BudgetSummary, RawCategoryAllocation, RawCostSavingIdea

DEFAULT_CATEGORIES = [
    ("Venue & Catering", 40.0, "Core venue booking, multi-course meal, drinks, and service staff"),
    ("Decor & Ambience", 15.0, "Floral arrangements, stage lighting, theme backdrops, table styling"),
    ("Photography & Video", 12.0, "Candid photography, cinematic highlights, drone shots, live streaming"),
    ("Entertainment & Sound", 10.0, "DJ/Emcee, sound equipment, stage performers, interactive activities"),
    ("Attire & Grooming", 8.0, "Host wardrobe, makeup artists, styling accessories"),
    ("Invitations & Favors", 4.0, "Digital invites, physical keepsakes, guest return gifts"),
    ("Logistics & Transport", 3.0, "Guest shuttles, parking attendants, luggage handling"),
    ("Contingency Buffer", 8.0, "Emergency reserve for last-minute headcount changes, weather shifts"),
]

def calculate_budget(
    total_budget: float,
    guest_count: int,
    currency: str,
    raw_allocations: List[RawCategoryAllocation] = None,
    raw_savings: List[RawCostSavingIdea] = None
) -> BudgetSummary:
    """
    Computes all budget arithmetic strictly in Python code.
    - Ensures exactly 100% total allocation.
    - Guarantees 5% - 10% contingency buffer.
    - Computes exact amounts, per-guest costs, and savings.
    """
    total_budget = round(float(total_budget), 2)
    guest_count = max(1, int(guest_count))
    
    # 1. Prepare raw percentage map
    category_weights: Dict[str, Tuple[float, str]] = {}
    
    if raw_allocations and len(raw_allocations) >= 3:
        for item in raw_allocations:
            cat_name = item.category.strip()
            # Prevent negative or infinite values
            raw_pct = max(0.5, float(item.raw_percentage))
            category_weights[cat_name] = (raw_pct, item.notes.strip() or f"Allocation for {cat_name}")
    else:
        for cat_name, pct, notes in DEFAULT_CATEGORIES:
            category_weights[cat_name] = (pct, notes)
            
    # 2. Check and enforce contingency buffer (5% - 10%)
    contingency_key = next((k for k in category_weights if "contingency" in k.lower() or "buffer" in k.lower()), None)
    if not contingency_key:
        contingency_key = "Contingency & Buffer"
        category_weights[contingency_key] = (8.0, "Reserved emergency fund for unanticipated costs")
    else:
        curr_pct, notes = category_weights[contingency_key]
        clamped_pct = max(5.0, min(10.0, curr_pct))
        category_weights[contingency_key] = (clamped_pct, notes)

    contingency_pct, contingency_note = category_weights[contingency_key]

    # 3. Normalize non-contingency categories to equal (100 - contingency_pct)
    non_contingency_keys = [k for k in category_weights if k != contingency_key]
    sum_non_contingency = sum(category_weights[k][0] for k in non_contingency_keys)
    
    target_non_contingency = 100.0 - contingency_pct
    
    normalized_percentages: Dict[str, float] = {}
    if sum_non_contingency > 0:
        for k in non_contingency_keys:
            raw_p = category_weights[k][0]
            normalized_percentages[k] = round((raw_p / sum_non_contingency) * target_non_contingency, 2)
    else:
        even_split = round(target_non_contingency / max(1, len(non_contingency_keys)), 2)
        for k in non_contingency_keys:
            normalized_percentages[k] = even_split

    normalized_percentages[contingency_key] = contingency_pct

    # Adjust rounding differences so sum of percentages is strictly 100.00%
    curr_sum = sum(normalized_percentages.values())
    diff = round(100.0 - curr_sum, 2)
    if diff != 0 and non_contingency_keys:
        # adjust the first non-contingency category
        first_key = non_contingency_keys[0]
        normalized_percentages[first_key] = round(normalized_percentages[first_key] + diff, 2)

    # 4. Compute exact amounts and per-guest figures in code
    items: List[BudgetItem] = []
    running_amount_sum = 0.0

    for idx, (cat_name, pct) in enumerate(normalized_percentages.items()):
        if idx == len(normalized_percentages) - 1:
            # Last item absorbs any 1-cent rounding difference
            amount = round(total_budget - running_amount_sum, 2)
        else:
            amount = round((total_budget * pct) / 100.0, 2)
            running_amount_sum += amount

        per_guest = round(amount / guest_count, 2)
        notes = category_weights[cat_name][1]
        
        items.append(BudgetItem(
            category=cat_name,
            percentage=pct,
            amount=amount,
            notes=notes,
            per_guest_amount=per_guest
        ))

    cost_per_guest = round(total_budget / guest_count, 2)
    contingency_amount = next((it.amount for it in items if it.category == contingency_key), round((total_budget * contingency_pct) / 100.0, 2))

    # 5. Programmatically compute Cost-Saving Ideas
    savings_list: List[CostSavingIdea] = []
    
    if raw_savings and len(raw_savings) > 0:
        for idx, s in enumerate(raw_savings[:5]):
            target = s.target_category.strip()
            # find category amount
            cat_match = next((c for c in items if target.lower() in c.category.lower() or c.category.lower() in target.lower()), items[0])
            pct_saved = max(2.0, min(35.0, float(s.savings_percent_of_category)))
            saved_amount = round((cat_match.amount * pct_saved) / 100.0, 2)
            
            savings_list.append(CostSavingIdea(
                id=f"saving-{idx+1}",
                title=s.title.strip(),
                description=s.description.strip(),
                target_category=cat_match.category,
                estimated_savings_percentage=pct_saved,
                estimated_savings_amount=saved_amount,
                tradeoff=s.tradeoff.strip()
            ))
    else:
        # Default programmatic cost saving ideas
        catering_cat = next((c for c in items if "catering" in c.category.lower() or "venue" in c.category.lower()), items[0])
        decor_cat = next((c for c in items if "decor" in c.category.lower()), items[1] if len(items) > 1 else items[0])
        photo_cat = next((c for c in items if "photo" in c.category.lower()), items[2] if len(items) > 2 else items[0])

        savings_list = [
            CostSavingIdea(
                id="saving-1",
                title="Seasonal & Local Menu Curations",
                description="Replace exotic off-season ingredients with fresh local gourmet specialties and interactive live counters.",
                target_category=catering_cat.category,
                estimated_savings_percentage=12.0,
                estimated_savings_amount=round((catering_cat.amount * 0.12), 2),
                tradeoff="Slightly fewer imported delicacies, but fresher taste and faster guest service."
            ),
            CostSavingIdea(
                id="saving-2",
                title="Strategic Lighting Over Heavy Floral Props",
                description="Use warm ambient up-lighting, fairy string canopies, and reusable brass lanterns instead of perishable exotic cut blooms.",
                target_category=decor_cat.category,
                estimated_savings_percentage=18.0,
                estimated_savings_amount=round((decor_cat.amount * 0.18), 2),
                tradeoff="Less monolithic flower walls, but far richer evening atmosphere and photographic depth."
            ),
            CostSavingIdea(
                id="saving-3",
                title="Hybrid Photography Package",
                description="Book principal photographers for core ceremonies and prime hours, utilizing cloud guest-upload QR codes for candid crowd coverage.",
                target_category=photo_cat.category,
                estimated_savings_percentage=15.0,
                estimated_savings_amount=round((photo_cat.amount * 0.15), 2),
                tradeoff="Requires active guest participation for crowd snaps, but yields authentic candid memories."
            )
        ]

    return BudgetSummary(
        total_budget=total_budget,
        currency=currency.upper(),
        guest_count=guest_count,
        cost_per_guest=cost_per_guest,
        allocated_total=total_budget,
        contingency_percentage=contingency_pct,
        contingency_amount=contingency_amount,
        categories=items,
        cost_saving_ideas=savings_list
    )
