"""
User Profile Manager
Manages user-specific data including preferences, pantry inventory, and interaction history.
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

USER_PROFILE_DIR = "data/user_profiles"

@dataclass
class UserPreferences:
    dietary_restrictions: List[str] = field(default_factory=list)
    disliked_ingredients: List[str] = field(default_factory=list)
    preferred_cuisines: List[str] = field(default_factory=list)

@dataclass
class PantryItem:
    name: str
    quantity: float
    unit: str

@dataclass
class UserProfile:
    user_id: str
    preferences: UserPreferences = field(default_factory=UserPreferences)
    pantry: List[PantryItem] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

class UserProfileManager:
    def __init__(self, storage_path: str = USER_PROFILE_DIR):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_profile_path(self, user_id: str) -> str:
        return os.path.join(self.storage_path, f"{user_id}.json")

    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        path = self._get_profile_path(user_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            preferences = UserPreferences(**data.get("preferences", {}))
            pantry = [PantryItem(**item) for item in data.get("pantry", [])]
            return UserProfile(
                user_id=user_id,
                preferences=preferences,
                pantry=pantry,
                history=data.get("history", []),
                created_at=data.get("created_at", datetime.now().isoformat())
            )

    def save_profile(self, profile: UserProfile) -> None:
        path = self._get_profile_path(profile.user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def create_profile(self, user_id: str) -> UserProfile:
        profile = UserProfile(user_id=user_id)
        self.save_profile(profile)
        return profile

    def add_to_pantry(self, user_id: str, item: PantryItem) -> None:
        profile = self.load_profile(user_id) or self.create_profile(user_id)
        profile.pantry.append(item)
        self.save_profile(profile)

    def update_preferences(self, user_id: str, new_prefs: Dict) -> None:
        profile = self.load_profile(user_id) or self.create_profile(user_id)
        for key, value in new_prefs.items():
            if hasattr(profile.preferences, key):
                setattr(profile.preferences, key, value)
        self.save_profile(profile)

    def log_recipe_use(self, user_id: str, recipe_id: str) -> None:
        profile = self.load_profile(user_id) or self.create_profile(user_id)
        profile.history.append(recipe_id)
        self.save_profile(profile)

    def remove_pantry_item(self, user_id: str, item_name: str) -> None:
        profile = self.load_profile(user_id) or self.create_profile(user_id)
        profile.pantry = [item for item in profile.pantry if item.name != item_name]
        self.save_profile(profile)

    def get_recent_history(self, user_id: str, limit: int = 5) -> List[str]:
        profile = self.load_profile(user_id)
        return profile.history[-limit:] if profile else []

    def get_pantry_items(self, user_id: str) -> List[PantryItem]:
        profile = self.load_profile(user_id)
        return profile.pantry if profile else []

    def delete_profile(self, user_id: str) -> None:
        path = self._get_profile_path(user_id)
        if os.path.exists(path):
            os.remove(path)
