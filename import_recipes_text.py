#!/usr/bin/env python3
"""
Import recipes from plain text notes (single or multiple recipes).

This avoids hand-writing long JSON/Python objects.

Accepted format (flexible):
  Title: One Pot Lemon Pasta
  Description: ...
  Prep Time: 10
  Cook Time: 15
  Servings: 4
  Cuisine: italian
  Difficulty: Easy
  Meal Type: dinner
  Tags: pasta, vegetarian, quick

  Ingredients:
  - 12 oz spaghetti
  - 2 tbsp olive oil
  - 3 cloves garlic, minced

  Instructions:
  1. Boil pasta until al dente.
  2. Saute garlic in olive oil.
  3. Toss together and serve.

Multiple recipes:
  separate each recipe block with a line containing only "===".

Run:
  ./venv/bin/python import_recipes_text.py --file data/recipes_from_notes.txt
  ./venv/bin/python import_recipes_text.py --file data/recipes_from_notes.txt --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from import_recipes_json import insert_batch

INGREDIENT_UNITS = {
    "cup", "cups", "tbsp", "tsp", "oz", "lb", "lbs", "g", "kg", "ml", "l",
    "clove", "cloves", "can", "cans", "pinch", "dash", "slice", "slices",
    "whole", "bunch", "package", "packages", "teaspoon", "teaspoons",
    "tablespoon", "tablespoons", "pound", "pounds",
}


def _parse_number(token: str) -> float | None:
    token = token.strip()
    if not token:
        return None
    if " " in token and "/" in token:
        # supports "1 1/2"
        whole, frac = token.split(" ", 1)
        try:
            a, b = frac.split("/", 1)
            return float(whole) + (float(a) / float(b))
        except Exception:
            return None
    if "/" in token:
        try:
            a, b = token.split("/", 1)
            return float(a) / float(b)
        except Exception:
            return None
    try:
        return float(token)
    except Exception:
        return None


def _parse_ingredient_line(line: str) -> dict[str, Any]:
    raw = re.sub(r"^\s*[-*]\s*", "", line).strip()
    raw = re.sub(r"^\s*\d+[\).\s-]*", "", raw).strip()
    if not raw:
        return {"name": "", "quantity": None, "unit": None}

    # e.g. "1 1/2 cups flour", "2 tbsp olive oil", "salt to taste"
    match = re.match(
        r"^(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)?\s*([a-zA-Z]+)?\s*(.+)$",
        raw,
    )
    if not match:
        return {"name": raw, "quantity": None, "unit": None}

    qty_token, unit, name = match.groups()
    qty = _parse_number(qty_token) if qty_token else None
    if not name or not name.strip():
        name = raw
    return {
        "name": name.strip(),
        "quantity": qty,
        "unit": unit.lower() if unit else None,
    }


def _looks_like_ingredient_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.match(r"^\s*\d+[\).]\s+", s):
        return False
    if re.match(r"^\s*[-*]\s+", s):
        return True
    # starts with numeric amount or vulgar fraction and usually unit/name
    if re.match(r"^\s*(\d+(?:\.\d+)?|\d+/\d+|¼|½|¾)\b", s):
        return True
    # rough "salt to taste", "olive oil"
    tokens = re.split(r"\s+", s.lower())
    if len(tokens) >= 2 and tokens[0] in INGREDIENT_UNITS:
        return True
    return False


def _looks_like_instruction_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.match(r"^\s*\d+[\).]\s+", s):
        return True
    first = s.split(" ", 1)[0].lower()
    common_verbs = {
        "add", "mix", "stir", "cook", "bake", "boil", "heat", "saute", "sauté",
        "whisk", "combine", "pour", "serve", "season", "simmer", "grill", "roast",
        "fold", "drizzle", "toss", "preheat", "chop", "slice",
    }
    return first in common_verbs


def _extract_time_minutes(text: str) -> int | None:
    m = re.search(r"(\d+)\s*(?:min|mins|minute|minutes)\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*(?:hr|hrs|hour|hours)\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 60
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return int(m.group(1))
    return None


def _extract_servings(text: str) -> int | None:
    m = re.search(r"(?:serves?|yield)\s*:?\s*(\d+)", text, re.IGNORECASE)
    if m:
        return max(1, int(m.group(1)))
    m = re.search(r"(\d+)\s*(?:servings?|people)", text, re.IGNORECASE)
    if m:
        return max(1, int(m.group(1)))
    return None


def _normalize_difficulty(value: str | None) -> str:
    v = (value or "").strip().lower()
    if v in {"easy", "e"}:
        return "Easy"
    if v in {"hard", "difficult", "h"}:
        return "Hard"
    return "Medium" if v == "medium" else "Easy"


def _split_blocks(text: str) -> list[str]:
    parts = re.split(r"(?m)^\s*===\s*$", text)
    return [p.strip() for p in parts if p.strip()]


def parse_recipe_block(block: str, idx: int) -> dict[str, Any]:
    lines = [ln.rstrip() for ln in block.splitlines()]

    recipe: dict[str, Any] = {
        "title": "",
        "description": "",
        "ingredients": [],
        "instructions": [],
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "difficulty": "Easy",
        "cuisine": "international",
        "tags": [],
    }
    meal_type = None
    mode = None  # None | ingredients | instructions

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        low = line.lower()
        if low in {"ingredients:", "ingredients", "what you need:", "you need:"}:
            mode = "ingredients"
            continue
        if low in {
            "instructions:",
            "instructions",
            "directions:",
            "directions",
            "method:",
            "method",
            "steps:",
            "steps",
            "how to make:",
        }:
            mode = "instructions"
            continue

        meta = re.match(
            r"^(title|description|prep time|cook time|total time|servings|cuisine|difficulty|meal type|tags)\s*:\s*(.+)$",
            line,
            re.IGNORECASE,
        )
        if meta:
            key = meta.group(1).strip().lower()
            val = meta.group(2).strip()
            mode = None
            if key == "title":
                recipe["title"] = val
            elif key == "description":
                recipe["description"] = val
            elif key == "prep time":
                parsed = _extract_time_minutes(val)
                if parsed is not None:
                    recipe["prep_time"] = parsed
            elif key == "cook time":
                parsed = _extract_time_minutes(val)
                if parsed is not None:
                    recipe["cook_time"] = parsed
            elif key == "total time":
                parsed = _extract_time_minutes(val)
                if parsed is not None:
                    # if no explicit prep/cook provided, keep it simple
                    if recipe["prep_time"] == 10 and recipe["cook_time"] == 20:
                        recipe["prep_time"] = 0
                        recipe["cook_time"] = parsed
            elif key == "servings":
                parsed = _extract_servings(val) or _extract_time_minutes(val)
                if parsed is not None:
                    recipe["servings"] = max(1, parsed)
            elif key == "cuisine":
                recipe["cuisine"] = val.lower()
            elif key == "difficulty":
                recipe["difficulty"] = _normalize_difficulty(val)
            elif key == "meal type":
                meal_type = val.lower()
            elif key == "tags":
                recipe["tags"] = [t.strip().lower() for t in val.split(",") if t.strip()]
            continue

        # tolerate messy metadata lines without colon
        prep_guess = re.match(r"^prep(?:\s*time)?\s+(.+)$", line, re.IGNORECASE)
        cook_guess = re.match(r"^cook(?:\s*time)?\s+(.+)$", line, re.IGNORECASE)
        total_guess = re.match(r"^total(?:\s*time)?\s+(.+)$", line, re.IGNORECASE)
        if prep_guess:
            parsed = _extract_time_minutes(prep_guess.group(1))
            if parsed is not None:
                recipe["prep_time"] = parsed
                continue
        if cook_guess:
            parsed = _extract_time_minutes(cook_guess.group(1))
            if parsed is not None:
                recipe["cook_time"] = parsed
                continue
        if total_guess and recipe["prep_time"] == 10 and recipe["cook_time"] == 20:
            parsed = _extract_time_minutes(total_guess.group(1))
            if parsed is not None:
                recipe["prep_time"] = 0
                recipe["cook_time"] = parsed
                continue

        servings_guess = _extract_servings(line)
        if servings_guess is not None:
            recipe["servings"] = servings_guess
            continue

        if line.lower().startswith("tags "):
            recipe["tags"] = [t.strip().lower() for t in line[5:].split(",") if t.strip()]
            continue

        if mode == "ingredients":
            ing = _parse_ingredient_line(line)
            if ing["name"]:
                recipe["ingredients"].append(ing)
            continue
        if mode == "instructions":
            step = re.sub(r"^\s*\d+[\).]\s*", "", line).strip()
            if step:
                recipe["instructions"].append(step)
            continue

        # heuristic section inference for messy copy-paste
        if _looks_like_instruction_line(line):
            recipe["instructions"].append(re.sub(r"^\s*\d+[\).]\s*", "", line).strip())
            continue
        if _looks_like_ingredient_line(line) and not recipe["instructions"]:
            recipe["ingredients"].append(_parse_ingredient_line(line))
            continue

        # Fallbacks:
        if not recipe["title"]:
            recipe["title"] = line
        elif not recipe["description"]:
            recipe["description"] = line

    if not recipe["title"]:
        recipe["title"] = f"Imported Recipe {idx + 1}"
    if not recipe["ingredients"]:
        raise ValueError(f"recipe[{idx}] '{recipe['title']}' has no ingredients")
    if not recipe["instructions"]:
        raise ValueError(f"recipe[{idx}] '{recipe['title']}' has no instructions")
    if meal_type:
        recipe["meal_type"] = meal_type

    return recipe


def parse_text_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    blocks = _split_blocks(text)
    return [parse_recipe_block(block, i) for i, block in enumerate(blocks)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Import recipes from plain text")
    ap.add_argument("--file", type=Path, required=True, help="Path to text file")
    ap.add_argument("--dry-run", action="store_true", help="Validate without writing DB")
    args = ap.parse_args()

    if not args.file.is_file():
        print(f"Not a file: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        recipes = parse_text_file(args.file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not recipes:
        print("No recipes found in text file.")
        sys.exit(0)

    print(f"Parsed {len(recipes)} recipe(s) from notes.")
    added, skipped, total = insert_batch(recipes, dry_run=args.dry_run)
    mode = "Dry run — " if args.dry_run else ""
    print(f"\n{mode}Added {added}, skipped {skipped} duplicates.")
    print(f"Total recipes in database: {total}")


if __name__ == "__main__":
    main()
