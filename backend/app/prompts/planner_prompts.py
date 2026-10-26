"""Prompts for EventGenie AI Event Planner Master Generation."""

PLANNER_SYSTEM_PROMPT = """You are EventGenie AI, a world-class luxury and budget event planner, cultural expert, and hospitality architect.
Your mission is to craft deeply personalized, culturally authentic, logistically sound, and breathtaking event blueprints.

CRITICAL OPERATIONAL RULES:
1. DO NOT PERFORM ARITHMETIC OR CALCULATE CALENDAR DATES. You will suggest normalized category weights (percentages from 1 to 100) and days_before_event offsets (e.g., 90, 60, 30, 14, 7, 1, 0, -1). All exact amounts, per-guest math, savings, and calendar dates will be computed strictly in Python code.
2. Ground all recommendations in the user's specific city/location (local vendors, typical regional venue styles, seasonal climate considerations like monsoons or peak winter wedding seasons).
3. Honor cultural nuances (e.g., Rajasthani, Punjabi, South Indian, Christian, Parsi, Jain dietary rules, tech college culture).
4. For budget allocation weights, ensure the category names include the core categories:
   - "Venue & Catering"
   - "Decor & Ambience"
   - "Photography & Videography"
   - "Entertainment & Music"
   - "Attire & Styling"
   - "Invitations & Favors"
   - "Logistics & Transport"
   - "Contingency Buffer"
5. For cost-saving ideas, suggest 3 to 5 clever, non-degrading hacks tailored specifically to this event type and city.
6. For vendor checklists, provide comprehensive checklists for at least 4 key categories (e.g., Venue, Catering, Photography, Decor/AV), with questions to ask, questions to confirm, negotiation tips, red flags, and a ready-to-dispatch WhatsApp/Email inquiry template!
7. Provide a detailed "AI Reasoning" breakdown explaining why this plan was designed this way (theme & cultural framing, budget strategy, seasonality & weather, guest experience focus, and risk mitigation).
8. Return ONLY valid JSON adhering strictly to the requested schema.
"""

FEW_SHOT_EXAMPLE_USER = """Event Type: wedding
City: Udaipur, India
Date: 2026-11-15
Guest Count: 120
Total Budget: 1500000 INR
Theme: Royal Mewar Heritage with Candlelight Lake View
Food Preference: veg
Setting: hybrid
Cultural Preferences: Traditional Rajasthani Pheras, vibrant Mehendi by lakeside, Royal Thali
Special Requests: Acoustic folk musicians, vintage car baraat entry, no single-use plastics"""

FEW_SHOT_EXAMPLE_ASSISTANT = """{
  "ai_reasoning": {
    "theme_and_cultural_framing": "Udaipur in mid-November offers glorious lakeside evenings. We framed this around Mewar royal heritage using brass urli centerpieces, live marigold garlands, and ambient candlelight rather than synthetic decor.",
    "budget_strategy": "With 120 guests and a 15 Lakh INR budget (approx 12,500/guest), we prioritize a memorable heritage Haveli venue and an unforgettable multi-course royal thali banquet, keeping 8% contingency for lakeside weather contingencies.",
    "seasonality_and_weather": "November in Rajasthan is peak wedding season with pleasant daytime temperatures (28°C) and brisk evenings (15°C). Outdoor lakeside dining requires patio heaters or bonfire alcoves.",
    "guest_experience_focus": "Intimate royal welcome with nagada drums, rose petal shower, interactive block-printing station during Mehendi, and custom brass camel mementos.",
    "risk_mitigation": "Secured indoor hall backup at the haveli in case of sudden November dew or lake breezes, and secured sound curfew permits for outdoor music past 10 PM."
  },
  "category_allocations": [
    {"category": "Venue & Catering", "raw_percentage": 42.0, "notes": "Heritage haveli rental, lakeside lawn, 4-course authentic Rajasthani & royal feast with live chaat"},
    {"category": "Decor & Ambience", "raw_percentage": 16.0, "notes": "Marigold canopies, Rajasthani puppets, terracotta diyas, candlelit lake reflections"},
    {"category": "Photography & Videography", "raw_percentage": 12.0, "notes": "2 candid photographers, 1 cinematic drone operator for baraat & sunset varmala"},
    {"category": "Entertainment & Music", "raw_percentage": 9.0, "notes": "Folk fusion acoustic band, live dhol players for baraat, traditional Ghoomar dancers"},
    {"category": "Attire & Styling", "raw_percentage": 6.0, "notes": "Traditional bridal poshak styling, turbans for baraatis, bridal makeup artist"},
    {"category": "Invitations & Favors", "raw_percentage": 4.0, "notes": "Handmade block-printed scroll e-invites, brass miniature camel keepsakes"},
    {"category": "Logistics & Transport", "raw_percentage": 3.0, "notes": "Vintage heritage car for groom entry, luggage golf carts for elderly guests"},
    {"category": "Contingency Buffer", "raw_percentage": 8.0, "notes": "Safety reserve for lake-permit licensing and last-minute room additions"}
  ],
  "cost_saving_ideas": [
    {
      "title": "Local Artisan Direct Sourcing for Marigolds",
      "description": "Source marigolds and jasmine directly from the Udaipur Mandi at 5 AM rather than through prime resort florists.",
      "target_category": "Decor & Ambience",
      "savings_percent_of_category": 20.0,
      "tradeoff": "Requires early morning pickup by a trusted family member or planner coordinator."
    },
    {
      "title": "Streamlined Royal Thali Course Structure",
      "description": "Consolidate to 24 curated regional Rajasthani dishes rather than an unmanageable 60-dish western-indian fusion spread.",
      "target_category": "Venue & Catering",
      "savings_percent_of_category": 12.0,
      "tradeoff": "Fewer international live pasta counters, but dramatically higher culinary authenticity and zero food waste."
    },
    {
      "title": "Digital Animated Video Invites + Seed Paper Keepsake",
      "description": "Send a cinematic WhatsApp motion graphic invite and distribute botanical seed-paper cards on arrival.",
      "target_category": "Invitations & Favors",
      "savings_percent_of_category": 35.0,
      "tradeoff": "No heavy hardbound gift boxes to courier, which guests frequently discard."
    }
  ],
  "timeline_tasks": [
    {"title": "Lock Heritage Haveli & Date Deposit", "description": "Inspect courtyard, confirm noise curfews, negotiate stay packages, sign agreement.", "days_before_event": 75, "phase": "Venue & Legal", "priority": "High", "owner_suggestion": "Host & Lead Coordinator"},
    {"title": "Catering Tasting & Regional Menu Finalization", "description": "Taste Dal Baati Churma, Ker Sangri, and live sweet counter items with the master chef.", "days_before_event": 45, "phase": "Food & Beverage", "priority": "High", "owner_suggestion": "Food Committee"},
    {"title": "Book Candid Cinematographer & Drone Pilot", "description": "Review Udaipur sunset portfolios and sign golden hour shoot schedule.", "days_before_event": 35, "phase": "Media", "priority": "Medium", "owner_suggestion": "Couple"},
    {"title": "Decor Walkthrough & Acoustic Lighting Setup", "description": "Test candle lanterns, up-lighting on stone jharokhas, and generator power backup.", "days_before_event": 20, "phase": "Production", "priority": "Medium", "owner_suggestion": "Decor Lead"},
    {"title": "Dispatch WhatsApp Animated Passes & RSVPs", "description": "Send personalized video links with Google Map directions to the lakeside venue.", "days_before_event": 14, "phase": "Guest Relations", "priority": "High", "owner_suggestion": "Host"},
    {"title": "Final Headcount Confirmation with Haveli Banquet", "description": "Freeze final plate count with 5% safety margin and finalize table seating.", "days_before_event": 7, "phase": "Operations", "priority": "High", "owner_suggestion": "Lead Planner"},
    {"title": "Full Sound Check & Baraat Vintage Car Test", "description": "Coordinate arrival timing of vintage car and dhol troupe.", "days_before_event": 1, "phase": "Rehearsal", "priority": "High", "owner_suggestion": "Stage Manager"},
    {"title": "Wedding Day Execution & Sunset Varmala Cues", "description": "Coordinate entry sequence, floral showers, buffet opening, and guest photo ops.", "days_before_event": 0, "phase": "Event Day", "priority": "High", "owner_suggestion": "All Team Leads"}
  ],
  "vendor_checklists": [
    {
      "id": "v-venue",
      "category": "Venue & Heritage Property",
      "what_to_ask": ["What is the exact outdoor amplified sound curfew (usually 10 PM)?", "Do you have dedicated high-voltage generator backups for stage lighting?", "Is outside catering allowed or are we locked to in-house vendors?"],
      "what_to_confirm": ["Bridal green room availability from 10 AM", "Dedicated valet parking space for 40+ vehicles", "Security guard allocation along the lakeside boundary"],
      "negotiation_tips": ["Request complimentary morning rooms for elderly guests", "Ask for venue cleanup and electricity surcharge waivers during contract signing"],
      "red_flags": ["Vague policies on corkage charges or mandatory sound vendor tie-ups", "No written indoor weather backup clause in case of rain"],
      "draft_inquiry_message": "Hello! We are planning a 120-guest wedding on Nov 15, 2026 in Udaipur. We would love to enquire about your haveli lawn and banquet availability, lawn hire rates, in-house catering packages, and outdoor curfew rules. Please share your brochure and wedding deck.",
      "completed_checks": []
    },
    {
      "id": "v-catering",
      "category": "Catering & Banquet",
      "what_to_ask": ["Can you prepare pure vegetarian food with separate Jain options?", "What is your server-to-guest ratio (ideal is 1 server per 10 guests for thali service)?", "Do you manage live beverage counters and drinking water dispensers?"],
      "what_to_confirm": ["Guaranteed live cooking stations with proper fume ventilation", "Food hygiene certifications and food warmer equipment", "Freshness guarantee for evening dairy sweets"],
      "negotiation_tips": ["Bundle evening welcome drinks and late-night tea counters into the per-plate cost", "Negotiate complimentary child plates (under 7 years)"],
      "red_flags": ["Refusal to offer a comprehensive pre-event tasting session", "Hidden charges for heating chafing dishes or trash disposal"],
      "draft_inquiry_message": "Namaste! We are looking for an exceptional pure-veg Rajasthani and North Indian catering service for 120 guests in Udaipur on Nov 15, 2026. Please share your royal thali menus, live counter options, and tasting availability.",
      "completed_checks": []
    }
  ],
  "creative_ideas": {
    "decor_concept": "Mewar Royal Splendor: Terracotta earthen lamps, brass Urlis floating with fresh yellow & orange marigolds, fairy-light canopies mirroring the calm lake surface, and hand-painted miniature motifs on seating easels.",
    "invitation_wording": "Together with our families, we invite you to join us beneath the starry skies of Mewar as Aarav & Meera unite in marriage. Your blessings are our greatest treasure.",
    "entertainment": [
      "Lakeside acoustic Santoor and flute performance during welcome drinks",
      "High-energy Dhol and brass band procession for the Baraat",
      "Interactive Ghoomar & Kalbelia folk performance where guests can join the circle"
    ],
    "games_and_activities": [
      "Live Mehendi artist booth with bespoke floral jewelry making",
      "Rajasthani Turban (Pagdi) tying competition for both families",
      "Heritage Polaroid guestbook where guests paste instant photos and write blessings"
    ],
    "return_gifts_favors": [
      "Hand-carved miniature brass elephants or camels with fragrant attar",
      "Artisan earthen jars of organic Rajasthan forest honey and roasted saffron nuts",
      "Plantable marigold seed cards with gratitude message"
    ],
    "curated_menu_highlights": [
      "Royal Dal Baati Churma with 3 varieties of hand-crushed churma (Rose, Besan, Dry Fruit)",
      "Smoked Ker Sangri Dakhor and Paneer Kundan Kalian in rich cashew gravy",
      "Live Jalebi & Rabdi counter served in miniature clay kulhads",
      "Welcome saffron-infused Thandai and tender coconut water shots"
    ],
    "photo_booth_concept": "Carved vintage wooden Jharokha window with Lake Pichola backdrop lighting, silk bolster cushions, and vintage umbrellas.",
    "signature_moment": "Sunset Varmala on a floating floral deck as traditional nagadas echo and cold-pyro sparklers illuminate the twilight sky."
  }
}"""
