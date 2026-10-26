import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from app.schemas.plan import EventRequest

def test_valid_event_request():
    """Verify that a properly structured event request validates successfully."""
    future_date = (date.today() + timedelta(days=20)).strftime("%Y-%m-%d")
    req = EventRequest(
        event_type="wedding",
        title="Royal Wedding",
        city="Udaipur",
        date=future_date,
        guest_count=150,
        total_budget=1500000.0,
        currency="INR",
        food_preference="veg",
        setting="hybrid"
    )
    assert req.guest_count == 150
    assert req.city == "Udaipur"

def test_past_date_rejected():
    """Verify that dates in the past are rejected with validation error."""
    past_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        EventRequest(
            event_type="birthday",
            city="Delhi",
            date=past_date,
            guest_count=20,
            total_budget=50000.0
        )

def test_empty_city_rejected():
    """Verify that an empty or whitespace city is rejected."""
    future_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    with pytest.raises(ValidationError):
        EventRequest(
            event_type="corporate",
            city="   ",
            date=future_date,
            guest_count=50,
            total_budget=100000.0
        )
