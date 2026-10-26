from datetime import datetime, date, timedelta, timezone
from typing import List
from app.schemas.plan import EventPlan

def generate_ics_calendar(plan: EventPlan) -> str:
    """
    Generates an RFC 5545 compliant iCalendar string containing
    all backward-planned deadlines and the main event day.
    """
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EventGenie AI//Event Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:EventGenie - {plan.request.title or plan.request.event_type.title()}",
        "X-WR-TIMEZONE:UTC"
    ]

    # Main event event
    event_date_str = plan.request.date.replace("-", "")
    # Next day for all-day event end
    try:
        e_date = datetime.strptime(plan.request.date, "%Y-%m-%d").date()
        next_day = (e_date + timedelta(days=1)).strftime("%Y%m%d")
    except Exception:
        next_day = event_date_str

    event_title = (plan.request.title or f"{plan.request.event_type.title()} Celebration").replace(",", "\\,").replace(";", "\\;")
    city = plan.request.city.replace(",", "\\,").replace(";", "\\;")

    lines.extend([
        "BEGIN:VEVENT",
        f"UID:main-event-{plan.id}@eventgenie.ai",
        f"DTSTAMP:{now_stamp}",
        f"DTSTART;VALUE=DATE:{event_date_str}",
        f"DTEND;VALUE=DATE:{next_day}",
        f"SUMMARY:⭐ {event_title} ({city})",
        f"DESCRIPTION:Target Event Day for {event_title} with {plan.request.guest_count} guests. Managed with EventGenie AI.",
        f"LOCATION:{city}",
        "PRIORITY:1",
        "STATUS:CONFIRMED",
        "END:VEVENT"
    ])

    # Add each timeline milestone
    for t in plan.timeline.tasks:
        d_str = t.deadline_date.replace("-", "")
        try:
            t_date = datetime.strptime(t.deadline_date, "%Y-%m-%d").date()
            t_next = (t_date + timedelta(days=1)).strftime("%Y%m%d")
        except Exception:
            t_next = d_str

        prio_val = 1 if t.priority == "High" else (5 if t.priority == "Medium" else 9)
        clean_title = t.title.replace(",", "\\,").replace(";", "\\;")
        clean_desc = f"{t.description} (Owner: {t.owner_suggestion}, Phase: {t.phase})".replace(",", "\\,").replace(";", "\\;")

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{t.id}-{plan.id}@eventgenie.ai",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{d_str}",
            f"DTEND;VALUE=DATE:{t_next}",
            f"SUMMARY:[{t.phase}] {clean_title}",
            f"DESCRIPTION:{clean_desc}",
            f"PRIORITY:{prio_val}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def generate_html_print_view(plan: EventPlan) -> str:
    """
    Renders an elegant, self-contained, print-ready HTML page for high-res PDF generation.
    """
    req = plan.request
    b = plan.budget
    t = plan.timeline
    c = plan.creative_ideas
    r = plan.ai_reasoning

    # Categories rows
    cat_rows = "".join([
        f"""<tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{item.category}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center;">{item.percentage}%</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{b.currency} {item.amount:,.2f}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">{b.currency} {item.per_guest_amount:,.2f}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 12px; color: #64748b;">{item.notes}</td>
        </tr>""" for item in b.categories
    ])

    # Tasks rows
    task_rows = "".join([
        f"""<tr>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{task.deadline_date}</td>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0;"><span style="background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-size: 11px;">{task.phase}</span></td>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{task.title}</td>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-size: 12px; color: #475569;">{task.description}</td>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: center;"><span style="color: {'#dc2626' if task.priority == 'High' else '#d97706'}; font-weight: 600;">{task.priority}</span></td>
            <td style="padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-size: 12px;">{task.owner_suggestion}</td>
        </tr>""" for task in t.tasks
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EventGenie AI Master Plan - {req.title or req.event_type.title()}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            line-height: 1.5;
            margin: 0;
            padding: 30px;
            background: #fff;
        }}
        .header {{
            border-bottom: 3px solid #6366f1;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .badge {{
            display: inline-block;
            background: #e0e7ff;
            color: #4338ca;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        h1 {{ margin: 10px 0 5px 0; font-size: 28px; color: #1e1b4b; }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .meta-item label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; }}
        .meta-item p {{ margin: 3px 0 0 0; font-size: 16px; font-weight: 700; color: #0f172a; }}
        .section-title {{ font-size: 18px; font-weight: 700; color: #312e81; border-left: 4px solid #6366f1; padding-left: 10px; margin: 30px 0 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th {{ background: #f1f5f9; text-align: left; padding: 10px; font-size: 12px; color: #475569; text-transform: uppercase; }}
        .reasoning-box {{ background: #fdf4ff; border: 1px solid #f0abfc; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .creative-card {{ background: #faf5ff; border: 1px solid #e9d5ff; padding: 15px; border-radius: 8px; margin-bottom: 12px; }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px; text-align: right;">
        <button onclick="window.print()" style="background: #4f46e5; color: white; border: none; padding: 10px 20px; font-weight: 600; border-radius: 6px; cursor: pointer;">
            🖨️ Print / Save as PDF
        </button>
    </div>

    <div class="header">
        <span class="badge">EventGenie AI Master Plan v{plan.version}</span>
        <h1>{req.title or (req.event_type.title() + ' Celebration')}</h1>
        <p style="color: #64748b; margin: 0;">Generated on {plan.created_at[:10]} • City: <strong>{req.city}</strong> • Date: <strong>{req.date}</strong></p>
    </div>

    <div class="meta-grid">
        <div class="meta-item"><label>Total Budget</label><p>{b.currency} {b.total_budget:,.2f}</p></div>
        <div class="meta-item"><label>Guest Count</label><p>{req.guest_count} Attendees</p></div>
        <div class="meta-item"><label>Cost Per Guest</label><p>{b.currency} {b.cost_per_guest:,.2f}</p></div>
        <div class="meta-item"><label>Contingency Buffer</label><p>{b.contingency_percentage}% ({b.currency} {b.contingency_amount:,.2f})</p></div>
    </div>

    <div class="reasoning-box">
        <h3 style="margin-top: 0; color: #86198f;">Why This Plan? (AI Strategic Grounding)</h3>
        <p><strong>Theme & Cultural Framing:</strong> {r.theme_and_cultural_framing}</p>
        <p><strong>Budget Strategy:</strong> {r.budget_strategy}</p>
        <p><strong>Seasonality & Climate:</strong> {r.seasonality_and_weather}</p>
    </div>

    <div class="section-title">1. Smart Budget Breakdown (Strict Code Arithmetic)</div>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th style="text-align: center;">% Share</th>
                <th style="text-align: right;">Amount</th>
                <th style="text-align: right;">Per Guest</th>
                <th>Strategic Notes</th>
            </tr>
        </thead>
        <tbody>
            {cat_rows}
        </tbody>
    </table>

    <div class="section-title">2. Programmatic Cost-Saving Opportunities</div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
        {''.join([f'''<div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 8px;">
            <strong style="color: #166534;">{s.title}</strong>
            <p style="font-size: 13px; margin: 6px 0; color: #15803d;">{s.description}</p>
            <p style="font-size: 12px; font-weight: 700; color: #166534; margin: 0;">Est. Savings: {b.currency} {s.estimated_savings_amount:,.2f} ({s.estimated_savings_percentage}%)</p>
        </div>''' for s in b.cost_saving_ideas])}
    </div>

    <div class="section-title">3. Backward-Planned Timeline ({'Compressed Rush Plan' if t.is_rush_plan else 'Comprehensive Schedule'})</div>
    <table>
        <thead>
            <tr>
                <th>Deadline</th>
                <th>Phase</th>
                <th>Task</th>
                <th>Details</th>
                <th style="text-align: center;">Priority</th>
                <th>Lead</th>
            </tr>
        </thead>
        <tbody>
            {task_rows}
        </tbody>
    </table>

    <div class="section-title">4. Creative Ideas & Signature Moments</div>
    <div class="creative-card">
        <strong>Decor & Atmosphere:</strong>
        <p style="margin: 4px 0 0 0;">{c.decor_concept}</p>
    </div>
    <div class="creative-card">
        <strong>Signature Moment:</strong>
        <p style="margin: 4px 0 0 0; color: #7e22ce; font-weight: 600;">{c.signature_moment}</p>
    </div>
    <div class="creative-card">
        <strong>Invitation Wording:</strong>
        <p style="margin: 4px 0 0 0; font-style: italic;">"{c.invitation_wording}"</p>
    </div>

    <footer style="margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 15px; text-align: center; font-size: 12px; color: #94a3b8;">
        Generated by EventGenie AI • Powered by Google GenAI Gemini • High-Fidelity Event Architecture
    </footer>
</body>
</html>"""
    return html
