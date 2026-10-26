from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str
    gemini_configured: bool
    firestore_configured: bool
    timestamp: str

class DemoScenario(BaseModel):
    id: str
    title: str
    subtitle: str
    icon: str
    data: Dict[str, Any]

DEMO_SCENARIOS: List[DemoScenario] = [
    DemoScenario(
        id="budget_wedding",
        title="Royal Budget Wedding",
        subtitle="150 Guests • Jaipur, India • ₹1,200,000",
        icon="sparkles",
        data={
            "event_type": "wedding",
            "title": "Aarav & Meera's Regal Heritage Wedding",
            "city": "Jaipur",
            "date": "2026-11-20",
            "guest_count": 150,
            "total_budget": 1200000,
            "currency": "INR",
            "theme": "Royal Rajasthani Heritage with Marigold & Terracotta accents",
            "food_preference": "veg",
            "setting": "hybrid",
            "cultural_preferences": "Traditional Rajasthani & Marwari customs, lively Sangeet and Pheras at twilight",
            "special_requests": "Drone photography for varmala, live folk fusion music, eco-friendly cloth signage"
        }
    ),
    DemoScenario(
        id="college_fest",
        title="Tech & Cultural College Fest",
        subtitle="500 Students • Bangalore, India • ₹500,000",
        icon="party-popper",
        data={
            "event_type": "college_fest",
            "title": "InnovateX & Pulse 2026",
            "city": "Bangalore",
            "date": "2026-12-05",
            "guest_count": 500,
            "total_budget": 500000,
            "currency": "INR",
            "theme": "Cyberpunk Neon & Innovation Playground",
            "food_preference": "mixed",
            "setting": "indoor",
            "cultural_preferences": "Pan-Indian energetic student crowd, dynamic battle of bands and hackathon night",
            "special_requests": "Heavy focus on high-energy sound & lighting, food trucks, digital QR passes, live streaming"
        }
    ),
    DemoScenario(
        id="kids_birthday",
        title="Cosmic Space Kid's Birthday",
        subtitle="30 Guests • Mumbai, India • ₹85,000",
        icon="rocket",
        data={
            "event_type": "birthday",
            "title": "Vihaan's 7th Galactic Explorer Mission",
            "city": "Mumbai",
            "date": "2026-10-31",
            "guest_count": 30,
            "total_budget": 850000,
            "currency": "INR",
            "theme": "Glow-in-the-dark Space Odyssey & Astronaut Academy",
            "food_preference": "veg",
            "setting": "indoor",
            "cultural_preferences": "Kid-friendly interactive games, DIY rocket workshop, custom astronaut mocktails",
            "special_requests": "Nut-free food menu for allergy safety, moon bounce castle, personalized astronaut ID return gifts"
        }
    )
]
