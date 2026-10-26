import json
import os
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.schemas.plan import EventPlan

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
LOCAL_STORAGE_FILE = os.path.join(DATA_DIR, "saved_plans.json")

class StorageService:
    def __init__(self):
        self.firestore_db = None
        self.in_memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Ensure local data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load_local_storage()

        # Try to initialize Firestore if configured
        if settings.USE_FIRESTORE and settings.GCP_PROJECT_ID:
            try:
                from google.cloud import firestore
                self.firestore_db = firestore.Client(
                    project=settings.GCP_PROJECT_ID,
                    database=settings.FIRESTORE_DATABASE_ID
                )
                logger.info("Connected to Google Cloud Firestore successfully.")
            except Exception as e:
                logger.warning(f"Firestore initialization failed ({e}). Using local in-memory fallback storage.")
                self.firestore_db = None
        else:
            logger.info("Firestore not configured or disabled; using resilient local storage.")

    def _load_local_storage(self):
        """Loads cached plans from local JSON file."""
        if os.path.exists(LOCAL_STORAGE_FILE):
            try:
                with open(LOCAL_STORAGE_FILE, "r", encoding="utf-8") as f:
                    self.in_memory_cache = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load local storage file: {e}")
                self.in_memory_cache = {}

    def _persist_local_storage(self):
        """Persists current plans cache to local JSON file."""
        try:
            with open(LOCAL_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.in_memory_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist to local storage file: {e}")

    def save_plan(self, plan: EventPlan) -> EventPlan:
        """Saves an event plan to Firestore or fallback store."""
        plan_dict = plan.model_dump()
        plan_id = plan.id

        if self.firestore_db:
            try:
                doc_ref = self.firestore_db.collection("event_plans").document(plan_id)
                doc_ref.set(plan_dict)
            except Exception as e:
                logger.warning(f"Firestore save error: {e}. Falling back to memory.")

        # Always update in-memory / local storage
        self.in_memory_cache[plan_id] = plan_dict
        self._persist_local_storage()
        return plan

    def get_plan(self, plan_id: str) -> Optional[EventPlan]:
        """Retrieves an event plan by ID."""
        if self.firestore_db:
            try:
                doc_ref = self.firestore_db.collection("event_plans").document(plan_id)
                doc = doc_ref.get()
                if doc.exists:
                    return EventPlan.model_validate(doc.to_dict())
            except Exception as e:
                logger.warning(f"Firestore read error: {e}")

        # Check in-memory cache
        plan_dict = self.in_memory_cache.get(plan_id)
        if plan_dict:
            return EventPlan.model_validate(plan_dict)
        return None

    def list_plans(self) -> List[Dict[str, Any]]:
        """Returns a list of saved plan summaries (id, title, city, date, budget, version, updated_at)."""
        summaries = []

        if self.firestore_db:
            try:
                docs = self.firestore_db.collection("event_plans").order_by("updated_at", direction="DESCENDING").limit(50).stream()
                for doc in docs:
                    d = doc.to_dict()
                    req = d.get("request", {})
                    b = d.get("budget", {})
                    summaries.append({
                        "id": d.get("id"),
                        "title": req.get("title") or req.get("event_type", "Event Plan"),
                        "event_type": req.get("event_type"),
                        "city": req.get("city"),
                        "date": req.get("date"),
                        "guest_count": req.get("guest_count"),
                        "total_budget": b.get("total_budget"),
                        "currency": b.get("currency", "INR"),
                        "version": d.get("version", 1),
                        "updated_at": d.get("updated_at")
                    })
                return summaries
            except Exception as e:
                logger.warning(f"Firestore list error: {e}")

        # Fallback in-memory list
        for p_id, d in sorted(self.in_memory_cache.items(), key=lambda x: x[1].get("updated_at", ""), reverse=True):
            req = d.get("request", {})
            b = d.get("budget", {})
            summaries.append({
                "id": d.get("id"),
                "title": req.get("title") or req.get("event_type", "Event Plan"),
                "event_type": req.get("event_type"),
                "city": req.get("city"),
                "date": req.get("date"),
                "guest_count": req.get("guest_count"),
                "total_budget": b.get("total_budget"),
                "currency": b.get("currency", "INR"),
                "version": d.get("version", 1),
                "updated_at": d.get("updated_at")
            })

        return summaries

    def delete_plan(self, plan_id: str) -> bool:
        """Deletes an event plan."""
        deleted = False
        if self.firestore_db:
            try:
                self.firestore_db.collection("event_plans").document(plan_id).delete()
                deleted = True
            except Exception as e:
                logger.warning(f"Firestore delete error: {e}")

        if plan_id in self.in_memory_cache:
            del self.in_memory_cache[plan_id]
            self._persist_local_storage()
            deleted = True

        return deleted

storage_service = StorageService()
