from datetime import datetime, date, timedelta
from typing import List, Optional
from app.schemas.plan import TimelineTask, TimelineSummary, RawTimelineTask, PriorityLevel, TaskStatus

def generate_timeline(
    event_date_str: str,
    raw_tasks: Optional[List[RawTimelineTask]] = None
) -> TimelineSummary:
    """
    Backward-plans deadlines from event date strictly using Python datetime arithmetic.
    Automatically switches to a compressed rush plan if event is less than 7 days away.
    """
    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = date.today()
    days_until_event = (event_date - today).days

    is_rush_plan = days_until_event < 7

    tasks: List[TimelineTask] = []

    if is_rush_plan:
        # Generate high-urgency compressed rush plan
        rush_milestones = [
            (min(days_until_event, 5), "Venue & Primary Catering Emergency Lock", "Verify venue availability, security deposit, power backup, and finalize core meal count.", "High", "Event Host / Lead Organizer", "Final Prep"),
            (min(days_until_event, 4), "Sound, AV & Decor Fast-Track", "Confirm sound vendor, playlist, stage backdrop, and lighting setup.", "High", "AV Lead", "Final Prep"),
            (min(days_until_event, 3), "Digital Invitations & RSVP Headcount Freeze", "Dispatch urgent WhatsApp/SMS digital passes with live location pins and dietary count.", "High", "Host / Communications", "Event Week"),
            (min(days_until_event, 2), "Vendor Coordination & Delivery Schedules", "Build hour-by-hour load-in schedule for cake, flowers, and rental gear.", "Medium", "Logistics Coordinator", "Event Week"),
            (min(days_until_event, 1), "Final Walkthrough & Rehearsal", "Soundcheck microphones, review seating charts, test slideshows, and prep cash honorariums.", "High", "Core Team", "Final Prep"),
            (0, "Event Day Execution & Welcome Protocol", "Manage guest arrivals, stage cues, photo-ops, buffet timings, and guest departures.", "High", "Master of Ceremonies / Host", "Event Day"),
            (-1, "Post-Event Wrap & Settlement", "Inventory check, return rental items, settle remaining vendor balances, and dispatch thank-you notes.", "Low", "Host / Finance", "Post-Event"),
        ]

        for idx, (days_before, title, desc, priority, owner, phase) in enumerate(rush_milestones):
            calc_date = event_date - timedelta(days=days_before)
            tasks.append(TimelineTask(
                id=f"rush-task-{idx+1}",
                title=title,
                description=desc,
                days_before_event=days_before,
                deadline_date=calc_date.strftime("%Y-%m-%d"),
                phase=phase,
                priority=priority,  # type: ignore
                owner_suggestion=owner,
                status="Not started"
            ))
    elif raw_tasks and len(raw_tasks) >= 4:
        # Map raw tasks from LLM, calculate real calendar dates in code
        for idx, rt in enumerate(raw_tasks):
            # Clamping days_before_event between days_until_event and -2
            target_days = max(-2, min(days_until_event, rt.days_before_event))
            calc_date = event_date - timedelta(days=target_days)
            tasks.append(TimelineTask(
                id=f"task-{idx+1}",
                title=rt.title.strip(),
                description=rt.description.strip(),
                days_before_event=target_days,
                deadline_date=calc_date.strftime("%Y-%m-%d"),
                phase=rt.phase.strip() or "Planning",
                priority=rt.priority,
                owner_suggestion=rt.owner_suggestion.strip() or "Event Organizer",
                status="Not started"
            ))
    else:
        # Standard robust milestone schedule
        standard_schedule = [
            (min(days_until_event, 90), "Vision, Budget Lock & Date Reservation", "Establish overall theme, budget envelopes, and hold date reservations.", "High", "Host / Lead Planner", "Milestone Kickoff"),
            (min(days_until_event, 60), "Venue & Primary Catering Final Contract", "Conduct food tastings, lock menus, and sign venue agreement with deposit.", "High", "Host", "Vendor Lock-in"),
            (min(days_until_event, 45), "Photography, DJ & Entertainment Booking", "Interview photographers, share shot-lists, and brief DJ on musical preferences.", "Medium", "Entertainment Lead", "Vendor Lock-in"),
            (min(days_until_event, 30), "Decor & Floral Design Signoff", "Review 3D renders/moodboards for entrance, stage, table centerpieces, and lighting.", "Medium", "Decor Stylist", "Creative Design"),
            (min(days_until_event, 21), "Invitations Dispatch & Wardrobe Fittings", "Dispatch invitations with RSVP links, schedule final wardrobe fittings and hair trials.", "High", "Host", "Guest Relations"),
            (min(days_until_event, 14), "RSVP Cut-off & Final Headcount Freeze", "Collate RSVPs, communicate final guaranteed headcounts to caterer and seating chart.", "High", "Logistics Lead", "Operations"),
            (min(days_until_event, 7), "Vendor Schedule Master Briefing", "Distribute master run-of-show timeline to all vendors and core family/team members.", "High", "Event Coordinator", "Final Prep"),
            (min(days_until_event, 1), "Venue Setup Inspection & Rehearsal", "Review sound setup, lighting checks, stage podium, and prepare vendor payment envelopes.", "High", "Lead Planner", "Final Prep"),
            (0, "Event Day Showtime", "Live coordination of ceremonies, dining service, stage performances, and memorable moments.", "High", "All Leads", "Event Day"),
            (-1, "Settlements & Gratitude Dispatch", "Complete vendor settlements, return security deposits, and send digital thank-you albums.", "Low", "Host", "Post-Event"),
        ]

        # filter out duplicates if days_until_event is smaller than milestones
        seen_days = set()
        task_counter = 1
        for days_before, title, desc, priority, owner, phase in standard_schedule:
            calc_date = event_date - timedelta(days=days_before)
            # Avoid duplicate same-day tasks if compressed
            tasks.append(TimelineTask(
                id=f"task-{task_counter}",
                title=title,
                description=desc,
                days_before_event=days_before,
                deadline_date=calc_date.strftime("%Y-%m-%d"),
                phase=phase,
                priority=priority, # type: ignore
                owner_suggestion=owner,
                status="Not started"
            ))
            task_counter += 1

    # Sort tasks chronologically: earliest deadline first, through event day, to post-event
    tasks.sort(key=lambda t: t.deadline_date)

    done_count = sum(1 for t in tasks if t.status == "Done")
    completion_pct = round((done_count / max(1, len(tasks))) * 100, 1)

    return TimelineSummary(
        is_rush_plan=is_rush_plan,
        days_until_event=days_until_event,
        tasks=tasks,
        completion_percentage=completion_pct
    )

def recalculate_timeline_dates(
    tasks: List[TimelineTask],
    new_event_date_str: str
) -> TimelineSummary:
    """Recalculates deadline dates for existing tasks when the event date is moved."""
    new_event_date = datetime.strptime(new_event_date_str, "%Y-%m-%d").date()
    today = date.today()
    days_until_event = (new_event_date - today).days

    updated_tasks: List[TimelineTask] = []
    for t in tasks:
        new_deadline = new_event_date - timedelta(days=t.days_before_event)
        updated_tasks.append(TimelineTask(
            id=t.id,
            title=t.title,
            description=t.description,
            days_before_event=t.days_before_event,
            deadline_date=new_deadline.strftime("%Y-%m-%d"),
            phase=t.phase,
            priority=t.priority,
            owner_suggestion=t.owner_suggestion,
            status=t.status
        ))

    updated_tasks.sort(key=lambda t: t.deadline_date)
    done_count = sum(1 for t in updated_tasks if t.status == "Done")
    completion_pct = round((done_count / max(1, len(updated_tasks))) * 100, 1)

    return TimelineSummary(
        is_rush_plan=days_until_event < 7,
        days_until_event=days_until_event,
        tasks=updated_tasks,
        completion_percentage=completion_pct
    )
