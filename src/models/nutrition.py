"""
Nutrition related Pydantic models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NutritionInfo(BaseModel):
    """Model for nutrition information"""
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    
    # Vitamins and minerals
    vitamin_c_mg: Optional[float] = Field(None, ge=0)
    calcium_mg: Optional[float] = Field(None, ge=0)
    iron_mg: Optional[float] = Field(None, ge=0)
    potassium_mg: Optional[float] = Field(None, ge=0)
    vitamin_a_iu: Optional[float] = Field(None, ge=0)
    vitamin_d_iu: Optional[float] = Field(None, ge=0)
    
    # Fat breakdown
    saturated_fat_g: Optional[float] = Field(None, ge=0)
    trans_fat_g: Optional[float] = Field(None, ge=0)
    monounsaturated_fat_g: Optional[float] = Field(None, ge=0)
    polyunsaturated_fat_g: Optional[float] = Field(None, ge=0)


class NutritionGoals(BaseModel):
    """Model for user nutrition goals"""
    calories: float = Field(default=2000, ge=800, le=5000)
    protein_g: float = Field(default=50, ge=20, le=300)
    carbs_g: float = Field(default=300, ge=50, le=500)
    fat_g: float = Field(default=65, ge=20, le=200)
    fiber_g: float = Field(default=25, ge=10, le=100)
    sodium_mg: float = Field(default=2300, ge=500, le=5000)
    sugar_g: Optional[float] = Field(default=50, ge=0, le=150)


class MacronutrientBreakdown(BaseModel):
    """Model for macronutrient percentage breakdown"""
    protein_percent: float = 0.0
    carbs_percent: float = 0.0
    fat_percent: float = 0.0


class NutritionScore(BaseModel):
    """Model for nutrition quality score"""
    score: int = Field(..., ge=0, le=100)
    grade: str  # A+, A, A-, B+, B, etc.
    description: str


class HealthIndicators(BaseModel):
    """Model for health indicators from nutrition"""
    protein: str
    fiber: str
    sodium: str
    sugar: str
    calories: str
    fat_quality: str
    micronutrients: str


class DietaryCompliance(BaseModel):
    """Model for dietary pattern compliance"""
    low_sodium: bool = False
    low_sugar: bool = False
    high_protein: bool = False
    high_fiber: bool = False
    low_cholesterol: bool = False
    low_saturated_fat: bool = False
    balanced_macros: bool = False
    heart_healthy: bool = False
    diabetic_friendly: bool = False


class NutrientDensity(BaseModel):
    """Model for nutrient density information"""
    score: int = Field(..., ge=0, le=100)
    grade: str  # A, B, C, D, F
    description: str
    density_scores: Dict[str, float] = Field(default_factory=dict)


class NutritionAnalysis(BaseModel):
    """Model for comprehensive nutrition analysis"""
    total_nutrition: NutritionInfo
    per_serving_nutrition: NutritionInfo
    macronutrient_breakdown: MacronutrientBreakdown
    nutrition_score: NutritionScore
    health_indicators: HealthIndicators
    dietary_compliance: DietaryCompliance
    nutrient_density: NutrientDensity
    servings: int
    analysis_date: datetime


class DailyNutritionSummary(BaseModel):
    """Model for daily nutrition tracking"""
    date: str
    total_nutrition: NutritionInfo
    goals: NutritionGoals
    goal_adherence: Dict[str, float] = Field(default_factory=dict)
    meals: list[Dict[str, Any]] = Field(default_factory=list)
    calories_remaining: float = 0.0
    protein_remaining: float = 0.0
    carbs_remaining: float = 0.0
    fat_remaining: float = 0.0

