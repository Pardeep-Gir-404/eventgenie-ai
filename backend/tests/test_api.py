from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Integration test for /api/health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "gemini_configured" in data

def test_get_demo_scenarios():
    """Integration test for /api/plan/demos."""
    response = client.get("/api/plan/demos")
    assert response.status_code == 200
    demos = response.json()
    assert len(demos) >= 3
    assert any(d["id"] == "budget_wedding" for d in demos)

def test_generate_plan_flow():
    """End-to-end integration test generating a plan via API."""
    future_date = (date.today() + timedelta(days=40)).strftime("%Y-%m-%d")
    payload = {
        "event_type": "birthday",
        "title": "Aanya's 5th Birthday Carnival",
        "city": "Pune",
        "date": future_date,
        "guest_count": 40,
        "total_budget": 120000.0,
        "currency": "INR",
        "theme": "Carnival & Fairground Circus",
        "food_preference": "veg",
        "setting": "indoor",
        "cultural_preferences": "Kid-friendly activities, cotton candy and balloon twisting",
        "special_requests": "Nut-free food menu"
    }
    response = client.post("/api/plan/generate", json=payload)
    assert response.status_code == 200
    plan = response.json()
    assert plan["id"].startswith("plan_")
    assert plan["budget"]["total_budget"] == 120000.0
    assert plan["budget"]["cost_per_guest"] == 3000.0
    assert len(plan["budget"]["categories"]) > 0
    assert len(plan["timeline"]["tasks"]) > 0
    assert len(plan["vendor_checklists"]) > 0
    assert "decor_concept" in plan["creative_ideas"]

def test_guardrail_blocks_unsafe_input():
    """Test that safety guardrails reject malicious or unsafe inputs."""
    future_date = (date.today() + timedelta(days=20)).strftime("%Y-%m-%d")
    payload = {
        "event_type": "other",
        "title": "Weapon Demonstration",
        "city": "Mumbai",
        "date": future_date,
        "guest_count": 50,
        "total_budget": 100000.0,
        "currency": "INR",
        "theme": "bomb and explosive showcase",
        "food_preference": "veg",
        "setting": "indoor"
    }
    response = client.post("/api/plan/generate", json=payload)
    assert response.status_code == 400
    assert "violates EventGenie AI's safety guidelines" in response.json()["detail"]
