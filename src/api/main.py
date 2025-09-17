from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid

# ---- import your modules
from src.core.recipe_importer import import_from_url, import_from_text, import_from_pdf  # adapt names
from src.core.search_engine import search_recipes
from src.core.shopping_list_generator import generate_shopping_list
from src.core.substitution_engine import suggest_substitutions
from src.core.recommendation_engine import RecommendationEngine
# from src.core.planner import build_meal_plan  # if you have it

app = FastAPI(title="Recipe Assistant API", version="0.1.0")

# ---- CORS for your Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Pydantic models
class Ingredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None

class Recipe(BaseModel):
    id: str
    title: str
    ingredients: List[Ingredient] = []
    steps: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ImportUrlRequest(BaseModel):
    url: str

class ImportTextRequest(BaseModel):
    text: str
    title: Optional[str] = None

class SearchRequest(BaseModel):
    q: str
    limit: int = 20

class PlannerRequest(BaseModel):
    start_date: str                 # "2025-09-10"
    days: int = 7
    dietary_prefs: List[str] = []   # ["vegetarian","low-carb"]
    exclude_ingredients: List[str] = []
    target_calories: Optional[int] = None

class ShoppingListRequest(BaseModel):
    recipe_ids: List[str]
    pantry_items: List[str] = []
    group_by_aisle: bool = True
    include_substitutions: bool = False

class SubstitutionRequest(BaseModel):
    ingredient: str
    diet: Optional[str] = None

# In-memory "db" for demo; replace with your real store later
_FAKE_DB: Dict[str, Recipe] = {}
_reco_engine = RecommendationEngine()  # if it needs config, pass it here

# ---- Health
@app.get("/api/health")
def health():
    return {"ok": True}

# ---- Import endpoints
@app.post("/api/import/url", response_model=Recipe)
def import_url(body: ImportUrlRequest):
    parsed = import_from_url(body.url)  # returns your internal recipe dict
    if not parsed:
        raise HTTPException(400, "Failed to import from URL")
    recipe_id = parsed.get("id") or str(uuid.uuid4())
    recipe = Recipe(id=recipe_id, **parsed | {"id": recipe_id})
    _FAKE_DB[recipe.id] = recipe
    return recipe

@app.post("/api/import/text", response_model=Recipe)
def import_text(body: ImportTextRequest):
    parsed = import_from_text(body.text, title=body.title)
    if not parsed:
        raise HTTPException(400, "Failed to import from text")
    recipe_id = parsed.get("id") or str(uuid.uuid4())
    recipe = Recipe(id=recipe_id, **parsed | {"id": recipe_id})
    _FAKE_DB[recipe.id] = recipe
    return recipe

@app.post("/api/import/pdf", response_model=Recipe)
async def import_pdf(file: UploadFile = File(...), title: str = Form(None)):
    pdf_bytes = await file.read()
    parsed = import_from_pdf(pdf_bytes, filename=file.filename, title=title)
    if not parsed:
        raise HTTPException(400, "Failed to import from PDF")
    recipe_id = parsed.get("id") or str(uuid.uuid4())
    recipe = Recipe(id=recipe_id, **parsed | {"id": recipe_id})
    _FAKE_DB[recipe.id] = recipe
    return recipe

# ---- Recipe detail
@app.get("/api/recipe/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: str):
    r = _FAKE_DB.get(recipe_id)
    if not r:
        raise HTTPException(404, "Recipe not found")
    return r

# ---- Search
@app.get("/api/search", response_model=List[Recipe])
def search(q: str, limit: int = 20):
    # bridge to your search_engine
    results = search_recipes(q=q, limit=limit)  # expect list of dicts
    recipes = []
    for item in results:
        rid = item.get("id") or str(uuid.uuid4())
        recipes.append(Recipe(id=rid, **item | {"id": rid}))
        _FAKE_DB[rid] = recipes[-1]
    return recipes

# ---- Planner (stub if you haven’t built it yet)
@app.post("/api/planner")
def planner(body: PlannerRequest):
    # plan = build_meal_plan(...)
    # return plan
    return {
        "start_date": body.start_date,
        "days": body.days,
        "meals": [],  # fill with your structure
        "notes": "Hook up src/core/planner.build_meal_plan(...) here"
    }

# ---- Shopping list
@app.post("/api/shopping-list")
def shopping_list(body: ShoppingListRequest):
    # get recipes from your real DB; here we reference _FAKE_DB
    selected = []
    for rid in body.recipe_ids:
        if rid in _FAKE_DB:
            selected.append(_FAKE_DB[rid].model_dump())
    result = generate_shopping_list(
        recipes=selected,
        pantry_items=set(body.pantry_items),
        group_by_aisle=body.group_by_aisle,
        include_substitutions=body.include_substitutions,
    )
    return result

# ---- Substitutions quick endpoint
@app.post("/api/substitutions")
def substitutions(body: SubstitutionRequest):
    return {"suggestions": suggest_substitutions(body.ingredient, diet=body.diet)}

# ---- Simple recommendations (optional)
@app.get("/api/recommendations", response_model=List[str])
def recommendations(user_id: Optional[str] = None, limit: int = 5):
    recs = _reco_engine.recommend_for_user(user_id=user_id, k=limit)
    return recs
