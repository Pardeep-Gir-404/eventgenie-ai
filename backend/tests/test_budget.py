import pytest
from app.services.budget_service import calculate_budget
from app.schemas.plan import RawCategoryAllocation, RawCostSavingIdea

def test_budget_percentages_sum_to_100():
    """Verify that normalized budget percentages strictly total 100.0%."""
    summary = calculate_budget(
        total_budget=1000000.0,
        guest_count=150,
        currency="INR"
    )
    total_pct = sum(item.percentage for item in summary.categories)
    assert round(total_pct, 2) == 100.0

def test_budget_amounts_sum_to_total():
    """Verify that category amounts sum strictly to total_budget."""
    total = 850000.0
    summary = calculate_budget(
        total_budget=total,
        guest_count=80,
        currency="INR"
    )
    allocated_sum = sum(item.amount for item in summary.categories)
    assert round(allocated_sum, 2) == round(total, 2)

def test_contingency_buffer_enforced():
    """Verify that contingency buffer is always between 5% and 10%."""
    # Test with low raw contingency
    raw_allocs = [
        RawCategoryAllocation(category="Venue", raw_percentage=50.0, notes="Venue"),
        RawCategoryAllocation(category="Food", raw_percentage=40.0, notes="Food"),
        RawCategoryAllocation(category="Contingency", raw_percentage=1.0, notes="Buffer")
    ]
    summary = calculate_budget(500000, 50, "INR", raw_allocations=raw_allocs)
    assert summary.contingency_percentage >= 5.0
    assert summary.contingency_percentage <= 10.0

def test_cost_per_guest_arithmetic():
    """Verify exact cost-per-guest division."""
    summary = calculate_budget(
        total_budget=150000.0,
        guest_count=30,
        currency="INR"
    )
    assert summary.cost_per_guest == 5000.0
    for it in summary.categories:
        assert it.per_guest_amount == round(it.amount / 30, 2)

def test_cost_saving_ideas_computation():
    """Verify that cost saving estimates are derived from category amounts."""
    summary = calculate_budget(
        total_budget=1200000.0,
        guest_count=100,
        currency="INR"
    )
    assert len(summary.cost_saving_ideas) >= 3
    for idea in summary.cost_saving_ideas:
        assert idea.estimated_savings_amount > 0
        assert idea.estimated_savings_percentage > 0
