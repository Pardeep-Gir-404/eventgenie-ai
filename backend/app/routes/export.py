from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse, PlainTextResponse

from app.services.firestore_service import storage_service
from app.services.export_service import generate_ics_calendar, generate_html_print_view

router = APIRouter(prefix="/api/export", tags=["Export & Share"])

@router.get("/{plan_id}/calendar.ics")
def download_calendar_ics(plan_id: str):
    """Downloads RFC 5545 compliant iCalendar .ics file containing all timeline deadlines."""
    plan = storage_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")

    ics_content = generate_ics_calendar(plan)
    filename = f"eventgenie_{plan_id}_schedule.ics"

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@router.get("/{plan_id}/pdf", response_class=HTMLResponse)
def get_pdf_print_view(plan_id: str):
    """Renders a beautiful standalone print-ready view for PDF export."""
    plan = storage_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")

    return HTMLResponse(content=generate_html_print_view(plan))

@router.get("/{plan_id}/share")
def get_shareable_plan(plan_id: str):
    """Provides public read-only access for shareable event links."""
    plan = storage_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
    return {
        "read_only": True,
        "share_url": f"/shared/{plan_id}",
        "plan": plan
    }
