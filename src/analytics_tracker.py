"""
Analytics Tracker Module
Logs user interactions, recipe usage, and system events for insights and monitoring.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

ANALYTICS_DIR = "data/analytics"
os.makedirs(ANALYTICS_DIR, exist_ok=True)


class AnalyticsTracker:
    def __init__(self, log_file: str = "interactions.jsonl"):
        self.log_path = os.path.join(ANALYTICS_DIR, log_file)

    def _log_event(self, event_type: str, user_id: Optional[str], payload: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "payload": payload
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def log_recipe_view(self, user_id: str, recipe_id: str):
        self._log_event("recipe_view", user_id, {"recipe_id": recipe_id})

    def log_recipe_cook(self, user_id: str, recipe_id: str):
        self._log_event("recipe_cooked", user_id, {"recipe_id": recipe_id})

    def log_rating(self, user_id: str, recipe_id: str, rating: float):
        self._log_event("recipe_rating", user_id, {"recipe_id": recipe_id, "rating": rating})

    def log_feedback(self, user_id: str, recipe_id: str, comment: str):
        self._log_event("recipe_feedback", user_id, {"recipe_id": recipe_id, "comment": comment})

    def log_timer_event(self, user_id: str, step_description: str, duration_sec: int, action: str):
        self._log_event("timer_event", user_id, {
            "step": step_description,
            "duration_seconds": duration_sec,
            "action": action  # e.g., start, pause, complete
        })

    def log_search(self, user_id: Optional[str], query: str):
        self._log_event("search", user_id, {"query": query})

    def log_substitution_used(self, user_id: Optional[str], ingredient: str, substitute: str):
        self._log_event("substitution", user_id, {"ingredient": ingredient, "substitute": substitute})

    def log_custom_event(self, user_id: Optional[str], event_name: str, data: Dict[str, Any]):
        self._log_event(event_name, user_id, data)
