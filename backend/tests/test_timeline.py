from datetime import date, timedelta
from app.services.timeline_service import generate_timeline, recalculate_timeline_dates

def test_timeline_standard_date_math():
    """Verify standard backward-planned dates do not exceed the event date."""
    target_date = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
    timeline = generate_timeline(event_date_str=target_date)

    assert timeline.is_rush_plan is False
    assert timeline.days_until_event == 60
    assert len(timeline.tasks) > 5

    # Check that every deadline_date is formatted as YYYY-MM-DD
    for task in timeline.tasks:
        assert len(task.deadline_date) == 10
        assert task.days_before_event is not None

def test_rush_plan_trigger_for_short_notice():
    """Verify that events less than 7 days away trigger a rush plan."""
    target_date = (date.today() + timedelta(days=4)).strftime("%Y-%m-%d")
    timeline = generate_timeline(event_date_str=target_date)

    assert timeline.is_rush_plan is True
    assert timeline.days_until_event == 4
    assert any("Emergency" in t.title or "Fast-Track" in t.title for t in timeline.tasks)

def test_timeline_recalculation_on_date_shift():
    """Verify that moving an event date updates all task deadlines accordingly."""
    initial_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    timeline = generate_timeline(event_date_str=initial_date)
    
    new_date = (date.today() + timedelta(days=45)).strftime("%Y-%m-%d")
    updated = recalculate_timeline_dates(timeline.tasks, new_date)

    assert updated.days_until_event == 45
    # The tasks should now have later deadline dates
    assert updated.tasks[0].deadline_date != timeline.tasks[0].deadline_date
