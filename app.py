"""
Recipe Assistant Web Application
Flask-based web interface for the Recipe Assistant
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid

# Import our existing modules
from src.recipe_assistant import RecipeAssistant
from src.recipe_database import RecipeDatabase
from src.utils import parse_ingredient_list, validate_recipe_data

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize our recipe system
recipe_assistant = RecipeAssistant()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_recipes():
    """Search recipes by ingredients"""
    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients', '').strip()
        
        if not ingredients_input:
            flash('Please enter some ingredients!', 'error')
            return render_template('search.html')
        
        # Parse ingredients
        ingredients = parse_ingredient_list(ingredients_input)
        
        # Find matching recipes
        matches = recipe_assistant.find_recipes_by_ingredients(ingredients)
        
        # Filter results with decent matches
        good_matches = [match for match in matches if match['match_percentage'] >= 20]
        
        return render_template('search_results.html', 
                             matches=good_matches, 
                             ingredients=ingredients,
                             search_term=ingredients_input)
    
    return render_template('search.html')

@app.route('/recipe/<recipe_id>')
def view_recipe(recipe_id):
    """View individual recipe details"""
    recipe = recipe_assistant.database.get_recipe(recipe_id)
    
    if not recipe:
        flash('Recipe not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('recipe_detail.html', recipe=recipe, recipe_id=recipe_id)

@app.route('/browse')
def browse_recipes():
    """Browse all recipes with filtering options"""
    filter_type = request.args.get('filter', 'all')
    filter_value = request.args.get('value', '')
    
    all_recipes = recipe_assistant.database.get_all_recipes()
    
    if filter_type == 'cuisine' and filter_value:
        filtered_recipes = recipe_assistant.database.search_recipes_by_cuisine(filter_value)
    elif filter_type == 'tag' and filter_value:
        filtered_recipes = recipe_assistant.database.search_recipes_by_tag(filter_value)
    else:
        filtered_recipes = all_recipes
    
    # Get available cuisines and tags for filter options
    cuisines = set()
    tags = set()
    
    for recipe in all_recipes.values():
        if 'cuisine' in recipe:
            cuisines.add(recipe['cuisine'])
        if 'tags' in recipe:
            tags.update(recipe['tags'])
    
    return render_template('browse.html', 
                         recipes=filtered_recipes,
                         cuisines=sorted(cuisines),
                         tags=sorted(tags),
                         current_filter=filter_type,
                         current_value=filter_value)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    """Add a new recipe"""
    if request.method == 'POST':
        # Get form data
        recipe_data = {
            'name': request.form.get('name', '').strip(),
            'ingredients': parse_ingredient_list(request.form.get('ingredients', '')),
            'instructions': [inst.strip() for inst in request.form.get('instructions', '').split('\n') if inst.strip()],
            'cook_time': request.form.get('cook_time', '').strip(),
            'difficulty': request.form.get('difficulty', 'Easy'),
            'servings': int(request.form.get('servings', 1)),
            'cuisine': request.form.get('cuisine', '').strip(),
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'created_at': datetime.now().isoformat(),
            'created_by': 'user'  # In future, this would be the logged-in user
        }
        
        # Validate recipe data
        is_valid, errors = validate_recipe_data(recipe_data)
        
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('add_recipe.html', recipe_data=recipe_data)
        
        # Generate recipe ID
        recipe_id = recipe_data['name'].lower().replace(' ', '_').replace('-', '_')
        recipe_id = ''.join(c for c in recipe_id if c.isalnum() or c == '_')
        
        # Ensure unique ID
        counter = 1
        original_id = recipe_id
        while recipe_assistant.database.get_recipe(recipe_id):
            recipe_id = f"{original_id}_{counter}"
            counter += 1
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{recipe_id}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                recipe_data['image'] = filename
        
        # Save recipe
        if recipe_assistant.database.add_recipe(recipe_id, recipe_data):
            flash(f'Recipe "{recipe_data["name"]}" added successfully!', 'success')
            return redirect(url_for('view_recipe', recipe_id=recipe_id))
        else:
            flash('Failed to save recipe. Please try again.', 'error')
    
    return render_template('add_recipe.html')

@app.route('/shopping_list')
def shopping_list():
    """Generate shopping list from selected recipes"""
    recipe_ids = request.args.getlist('recipes')
    
    if not recipe_ids:
        flash('No recipes selected for shopping list!', 'error')
        return redirect(url_for('browse_recipes'))
    
    # Collect all ingredients from selected recipes
    shopping_items = {}
    selected_recipes = []
    
    for recipe_id in recipe_ids:
        recipe = recipe_assistant.database.get_recipe(recipe_id)
        if recipe:
            selected_recipes.append({'id': recipe_id, 'name': recipe['name']})
            
            for ingredient in recipe['ingredients']:
                ingredient_lower = ingredient.lower()
                if ingredient_lower in shopping_items:
                    shopping_items[ingredient_lower]['count'] += 1
                    shopping_items[ingredient_lower]['recipes'].append(recipe['name'])
                else:
                    shopping_items[ingredient_lower] = {
                        'name': ingredient,
                        'count': 1,
                        'recipes': [recipe['name']]
                    }
    
    return render_template('shopping_list.html', 
                         shopping_items=shopping_items,
                         selected_recipes=selected_recipes)

@app.route('/api/recipes')
def api_recipes():
    """API endpoint to get all recipes as JSON"""
    recipes = recipe_assistant.database.get_all_recipes()
    return jsonify(recipes)

@app.route('/api/search')
def api_search():
    """API endpoint for recipe search"""
    ingredients = request.args.get('ingredients', '').strip()
    
    if not ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    ingredient_list = parse_ingredient_list(ingredients)
    matches = recipe_assistant.find_recipes_by_ingredients(ingredient_list)
    
    # Convert to JSON-serializable format
    results = []
    for match in matches:
        if match['match_percentage'] >= 20:  # Only include decent matches
            results.append({
                'recipe_id': match['recipe_id'],
                'name': match['recipe']['name'],
                'match_percentage': round(match['match_percentage'], 1),
                'cook_time': match['recipe']['cook_time'],
                'difficulty': match['recipe']['difficulty'],
                'missing_ingredients': match['missing_ingredients']
            })
    
    return jsonify(results)

@app.route('/meal_planner')
def meal_planner():
    """Weekly meal planning interface"""
    return render_template('meal_planner.html')

@app.route('/favorites')
def favorites():
    """User's favorite recipes (stored in session for now)"""
    favorite_ids = session.get('favorites', [])
    favorite_recipes = {}
    
    for recipe_id in favorite_ids:
        recipe = recipe_assistant.database.get_recipe(recipe_id)
        if recipe:
            favorite_recipes[recipe_id] = recipe
    
    return render_template('favorites.html', recipes=favorite_recipes)

@app.route('/toggle_favorite/<recipe_id>')
def toggle_favorite(recipe_id):
    """Add/remove recipe from favorites"""
    favorites = session.get('favorites', [])
    
    if recipe_id in favorites:
        favorites.remove(recipe_id)
        action = 'removed from'
    else:
        favorites.append(recipe_id)
        action = 'added to'
    
    session['favorites'] = favorites
    flash(f'Recipe {action} favorites!', 'success')
    
    return redirect(request.referrer or url_for('view_recipe', recipe_id=recipe_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)