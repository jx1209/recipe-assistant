"""
Recipe Rating and Feedback System
Allows users to rate recipes and leave comments, with support for updates and querying.
"""

import json
import os
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict, field
from datetime import datetime

FEEDBACK_DIR = "data/feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)


@dataclass
class RatingEntry:
    user_id: str
    rating: float  # 1.0 to 5.0
    comment: Optional[str] = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


class FeedbackManager:
    def __init__(self, feedback_dir: str = FEEDBACK_DIR):
        self.feedback_dir = feedback_dir

    def _get_feedback_path(self, recipe_id: str) -> str:
        return os.path.join(self.feedback_dir, f"{recipe_id}.json")

    def load_feedback(self, recipe_id: str) -> List[RatingEntry]:
        path = self._get_feedback_path(recipe_id)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return [RatingEntry(**entry) for entry in raw]

    def save_feedback(self, recipe_id: str, feedback: List[RatingEntry]) -> None:
        path = self._get_feedback_path(recipe_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([entry.to_dict() for entry in feedback], f, indent=2)

    def submit_feedback(self, recipe_id: str, user_id: str, rating: float, comment: Optional[str] = ""):
        assert 1.0 <= rating <= 5.0, "Rating must be between 1.0 and 5.0"
        feedback = self.load_feedback(recipe_id)

        # Overwrite previous feedback from this user if it exists
        feedback = [f for f in feedback if f.user_id != user_id]
        feedback.append(RatingEntry(user_id=user_id, rating=rating, comment=comment))
        self.save_feedback(recipe_id, feedback)

    def get_average_rating(self, recipe_id: str) -> Optional[float]:
        feedback = self.load_feedback(recipe_id)
        if not feedback:
            return None
        return round(sum(f.rating for f in feedback) / len(feedback), 2)

    def get_comments(self, recipe_id: str) -> List[Dict[str, str]]:
        feedback = self.load_feedback(recipe_id)
        return [
            {"user_id": f.user_id, "comment": f.comment, "rating": f.rating, "timestamp": f.timestamp}
            for f in feedback if f.comment
        ]

    def get_user_feedback(self, recipe_id: str, user_id: str) -> Optional[RatingEntry]:
        feedback = self.load_feedback(recipe_id)
        for f in feedback:
            if f.user_id == user_id:
                return f
        return None

    def delete_user_feedback(self, recipe_id: str, user_id: str) -> bool:
        feedback = self.load_feedback(recipe_id)
        new_feedback = [f for f in feedback if f.user_id != user_id]
        if len(new_feedback) != len(feedback):
            self.save_feedback(recipe_id, new_feedback)
            return True
        return False
