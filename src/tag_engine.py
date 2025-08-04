"""
Tag Engine
Automatically assigns descriptive tags to recipes using ingredients and instructions.
"""

import re
import spacy
from typing import List, Dict, Optional

# Load spaCy language model (small size is fast & sufficient)
# Run: python -m spacy download en_core_web_sm if not already installed
nlp = spacy.load("en_core_web_sm")


class TagEngine:
    def __init__(self):
        self.keyword_tags: Dict[str, List[str]] = {
            "vegetarian": ["tofu", "tempeh", "beans", "cheese", "milk", "vegetable", "lentil", "egg", "chickpeas"],
            "vegan": ["tofu", "tempeh", "plant milk", "nutritional yeast", "chickpeas", "lentils"],
            "gluten-free": ["rice", "quinoa", "corn", "polenta", "gluten-free", "buckwheat"],
            "keto": ["almond flour", "coconut oil", "cheese", "eggs", "meat", "avocado", "olive oil"],
            "spicy": ["chili", "jalapeno", "hot sauce", "cayenne", "sriracha"],
            "sweet": ["sugar", "honey", "maple syrup", "chocolate", "cinnamon"],
            "quick": ["microwave", "5 minutes", "quick", "easy", "instant"],
            "breakfast": ["eggs", "pancake", "oatmeal", "toast", "cereal"],
            "dinner": ["roast", "pasta", "steak", "lasagna", "stew", "bake"],
            "healthy": ["grilled", "baked", "steamed", "quinoa", "vegetable", "salad"],
        }

    def assign_tags(self, title: str, ingredients: List[str], instructions: List[str]) -> List[str]:
        """
        Assign tags based on recipe content.
        """
        tags = set()
        text = " ".join([title] + ingredients + instructions).lower()
        doc = nlp(text)

        for tag, keywords in self.keyword_tags.items():
            for word in keywords:
                # Match keyword or lemmatized version
                if word in text or any(word in token.lemma_ for token in doc):
                    tags.add(tag)
                    break

        return sorted(tags)

    def add_custom_tag(self, tag_name: str, keywords: List[str]):
        self.keyword_tags[tag_name.lower()] = keywords

    def get_all_tags(self) -> List[str]:
        return sorted(self.keyword_tags.keys())
