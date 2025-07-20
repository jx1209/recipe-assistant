import json
import random
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class RecommendationEngine:
    def __init__(self, recipe_data: Dict[str, Dict], interaction_log_path: str = "data/user_interactions.json"):
        self.recipes = recipe_data
        self.interaction_log_path = Path(interaction_log_path)
        self.user_history = defaultdict(list)
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._tfidf_matrix = self._build_tfidf_matrix()
        self._load_interactions()

    def _build_tfidf_matrix(self):
        documents = []
        for recipe in self.recipes.values():
            text = recipe.get("name", "") + " " + \
                   " ".join(recipe.get("ingredients", [])) + " " + \
                   " ".join(recipe.get("tags", []))
            documents.append(text)
        return self._vectorizer.fit_transform(documents)

    def _load_interactions(self):
        if self.interaction_log_path.exists():
            with open(self.interaction_log_path, "r", encoding="utf-8") as f:
                self.user_history = defaultdict(list, json.load(f))

    def _save_interactions(self):
        with open(self.interaction_log_path, "w", encoding="utf-8") as f:
            json.dump(self.user_history, f, indent=2)

    def log_interaction(self, user_id: str, recipe_id: str, action: str):
        self.user_history[user_id].append({"recipe_id": recipe_id, "action": action})
        self._save_interactions()

    def get_similar_recipes(self, recipe_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
        try:
            index = list(self.recipes.keys()).index(recipe_id)
        except ValueError:
            return []

        sims = cosine_similarity(self._tfidf_matrix[index], self._tfidf_matrix).flatten()
        scored = [(rid, sims[i]) for i, rid in enumerate(self.recipes.keys()) if rid != recipe_id]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def recommend_based_on_history(self, user_id: str, top_n: int = 5) -> List[str]:
        if user_id not in self.user_history:
            return self.recommend_random(top_n)

        liked = [r["recipe_id"] for r in self.user_history[user_id] if r["action"] in ("liked", "cooked")]
        candidate_scores = Counter()

        for rid in liked:
            for similar_rid, score in self.get_similar_recipes(rid, 10):
                candidate_scores[similar_rid] += score

        for r in liked:
            candidate_scores.pop(r, None)

        return [r for r, _ in candidate_scores.most_common(top_n)]

    def recommend_by_context(self, dietary_pref: Optional[str] = None, cuisine: Optional[str] = None,
                             tag: Optional[str] = None, top_n: int = 5) -> List[str]:
        filtered = self.recipes.copy()
        if dietary_pref:
            filtered = {k: v for k, v in filtered.items()
                        if dietary_pref.lower() in [t.lower() for t in v.get("tags", [])]}
        if cuisine:
            filtered = {k: v for k, v in filtered.items()
                        if cuisine.lower() == v.get("cuisine", "").lower()}
        if tag:
            filtered = {k: v for k, v in filtered.items()
                        if tag.lower() in [t.lower() for t in v.get("tags", [])]}

        return random.sample(list(filtered.keys()), min(top_n, len(filtered)))

    def recommend_random(self, top_n: int = 5) -> List[str]:
        return random.sample(list(self.recipes.keys()), min(top_n, len(self.recipes)))

    def get_weekly_recommendation(self, user_id: str) -> Dict[str, List[str]]:
        history = self.recommend_based_on_history(user_id, top_n=2)
        similar = [r for rid in history for r, _ in self.get_similar_recipes(rid, 2)]
        seasonal = self.recommend_by_context(tag="summer", top_n=2)
        randoms = self.recommend_random(top_n=1)

        combined = list(dict.fromkeys(history + similar + seasonal + randoms))
        return {"weekly_plan": combined[:7]}
