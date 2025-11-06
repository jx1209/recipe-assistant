"""
Test Suite for Recipe Assistant
Run these tests to ensure the application works correctly
"""

import unittest
import sys
import os
import tempfile
import json

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from recipe_database import RecipeDatabase
from utils import (
    calculate_ingredient_similarity,
    clean_ingredient_name,
    validate_recipe_data,
    parse_ingredient_list,
    get_recipe_id_from_name
)