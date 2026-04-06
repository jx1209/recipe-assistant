#!/usr/bin/env python3
"""
Bulk-import recipes from JSON files (append-only; skips existing titles).

You maintain data/recipes_to_import.json (or any path) instead of editing Python.

Supported inputs:
  - A JSON array of recipe objects
  - JSON Lines: one recipe object per line
  - A directory: every *.json file is loaded and merged (each file can be an array or one object)

Ingredient amounts: use "quantity" or "amount" (both map to stored quantity).

Run from project root:
  ./venv/bin/python import_recipes_json.py --file data/recipes_to_import.json
  ./venv/bin/python import_recipes_json.py --dir ./my_recipes/
  ./venv/bin/python import_recipes_json.py --file data/recipes_to_import.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from src.database import get_db

settings = get_settings()


def _normalize_ingredient(raw: dict[str, Any]) -> dict[str, Any]:
    name = (raw.get("name") or "").strip()
    if not name:
        raise ValueError("ingredient missing name")
    q = raw.get("quantity")
    if q is None and "amount" in raw:
        q = raw["amount"]
    return {"name": name, "quantity": q, "unit": raw.get("unit")}


def _ingredients_json(recipe: dict[str, Any]) -> str:
    rows = []
    for ing in recipe["ingredients"]:
        n = _normalize_ingredient(ing if isinstance(ing, dict) else {})
        rows.append(
            {"name": n["name"], "quantity": n["quantity"], "unit": n.get("unit")}
        )
    return json.dumps(rows)


def _parse_json_blob(text: str) -> List[dict[str, Any]]:
    text = text.strip()
    if not text:
        return []
    # JSON array
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("root JSON must be an array")
        return [x for x in data if isinstance(x, dict)]
    # JSON Lines
    out: List[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if isinstance(obj, dict):
            out.append(obj)
    return out


def load_recipes_from_file(path: Path) -> List[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    recipes = _parse_json_blob(text)
    if not recipes and text.strip():
        # single object
        obj = json.loads(text)
        if isinstance(obj, dict):
            recipes = [obj]
    return recipes


def load_recipes_from_dir(dir_path: Path) -> List[dict[str, Any]]:
    merged: List[dict[str, Any]] = []
    for p in sorted(dir_path.glob("*.json")):
        merged.extend(load_recipes_from_file(p))
    return merged


def validate_recipe(r: dict[str, Any], ctx: str) -> None:
    required = [
        "title",
        "ingredients",
        "instructions",
        "prep_time",
        "cook_time",
        "servings",
        "difficulty",
        "cuisine",
    ]
    missing = [k for k in required if k not in r]
    if missing:
        raise ValueError(f"{ctx}: missing keys: {', '.join(missing)}")
    if not r["ingredients"]:
        raise ValueError(f"{ctx}: ingredients must be non-empty")
    if not r["instructions"]:
        raise ValueError(f"{ctx}: instructions must be non-empty")


def insert_batch(
    recipes: List[dict[str, Any]], *, dry_run: bool
) -> tuple[int, int, int]:
    db = get_db(settings.DATABASE_URL)
    cur = db.conn.cursor()
    cur.execute("SELECT id FROM users LIMIT 1")
    row = cur.fetchone()
    if not row:
        print("No user found. Create a user first or run populate_recipes on empty DB.")
        sys.exit(1)
    user_id = row["id"]

    added = 0
    skipped = 0
    for i, recipe in enumerate(recipes):
        ctx = f"recipe[{i}] ({recipe.get('title', '?')})"
        validate_recipe(recipe, ctx)

        title = str(recipe["title"]).strip()
        cur.execute(
            "SELECT 1 FROM recipes WHERE LOWER(title) = LOWER(?) AND is_deleted = 0",
            (title,),
        )
        if cur.fetchone():
            skipped += 1
            print(f"  skip (exists): {title}")
            continue

        total_time = int(recipe["prep_time"]) + int(recipe["cook_time"])
        description = recipe.get("description") or ""

        if dry_run:
            added += 1
            print(f"  [dry-run] would add: {title}")
            continue

        cur.execute(
            """
            INSERT INTO recipes (
                created_by, title, description, source_url, source_name,
                ingredients_json, instructions_json,
                image_url, prep_time_minutes, cook_time_minutes, total_time_minutes,
                servings, difficulty, cuisine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                description,
                recipe.get("source_url"),
                recipe.get("source_name"),
                _ingredients_json(recipe),
                json.dumps(recipe["instructions"]),
                recipe.get("image_url"),
                int(recipe["prep_time"]),
                int(recipe["cook_time"]),
                total_time,
                int(recipe["servings"]),
                recipe["difficulty"],
                recipe["cuisine"],
            ),
        )
        rid = cur.lastrowid
        tag_set = {t.lower().strip() for t in recipe.get("tags", []) if t}
        mt = recipe.get("meal_type")
        if mt:
            tag_set.add(str(mt).lower().strip())
        for tag in sorted(tag_set):
            try:
                cur.execute(
                    "INSERT INTO recipe_tags (recipe_id, tag_name) VALUES (?, ?)",
                    (rid, tag),
                )
            except Exception:
                pass
        added += 1
        print(f"  + {title}")

    if not dry_run:
        db.conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM recipes WHERE is_deleted = 0")
    total_row = cur.fetchone()
    total = total_row["c"] if total_row else 0
    return added, skipped, total


def main() -> None:
    ap = argparse.ArgumentParser(description="Import recipes from JSON")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", type=Path, help="Path to .json (array, JSONL, or single object)")
    g.add_argument("--dir", type=Path, help="Directory of *.json files")
    ap.add_argument("--dry-run", action="store_true", help="Validate without writing DB")
    args = ap.parse_args()

    if args.file:
        if not args.file.is_file():
            print(f"Not a file: {args.file}", file=sys.stderr)
            sys.exit(1)
        recipes = load_recipes_from_file(args.file)
    else:
        assert args.dir is not None
        if not args.dir.is_dir():
            print(f"Not a directory: {args.dir}", file=sys.stderr)
            sys.exit(1)
        recipes = load_recipes_from_dir(args.dir)

    if not recipes:
        print("No recipes found in input.")
        sys.exit(0)

    print(f"Loaded {len(recipes)} recipe(s) from input.")
    try:
        added, skipped, total = insert_batch(recipes, dry_run=args.dry_run)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    mode = "Dry run — " if args.dry_run else ""
    print(f"\n{mode}Added {added}, skipped {skipped} duplicates.")
    print(f"Total recipes in database: {total}")


if __name__ == "__main__":
    main()
