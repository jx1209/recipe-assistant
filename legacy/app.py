import os
import json
import logging
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler

from src.recipe_assistant import RecipeAssistant
from src.recipe_database import RecipeDatabase
from src.utils.util_funcs import parse_ingredient_list, validate_recipe_data

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    handler = RotatingFileHandler('logs/recipe_assistant.log', maxBytes=10240, backupCount=10)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

    recipe_assistant = RecipeAssistant()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['GET', 'POST'])
    def search_recipes():
        if request.method == 'POST':
            ingredients_input = request.form.get('ingredients', '').strip()
            if not ingredients_input:
                flash('Please enter some ingredients.', 'error')
                return render_template('search.html')
            ingredients = parse_ingredient_list(ingredients_input)
            matches = recipe_assistant.find_recipes_by_ingredients(ingredients)
            results = [m for m in matches if m['match_percentage'] >= 20]
            return render_template('search_results.html', matches=results, ingredients=ingredients, search_term=ingredients_input)
        return render_template('search.html')

    @app.route('/recipe/<recipe_id>')
    def view_recipe(recipe_id):
        recipe = recipe_assistant.database.get_recipe(recipe_id)
        if not recipe:
            flash('Recipe not found.', 'error')
            return redirect(url_for('index'))
        return render_template('recipe_detail.html', recipe=recipe, recipe_id=recipe_id)

    @app.route('/browse')
    def browse_recipes():
        filter_type = request.args.get('filter', 'all')
        filter_value = request.args.get('value', '')
        all_recipes = recipe_assistant.database.get_all_recipes()

        if filter_type == 'cuisine' and filter_value:
            filtered = recipe_assistant.database.search_recipes_by_cuisine(filter_value)
        elif filter_type == 'tag' and filter_value:
            filtered = recipe_assistant.database.search_recipes_by_tag(filter_value)
        else:
            filtered = all_recipes

        cuisines, tags = set(), set()
        for r in all_recipes.values():
            if 'cuisine' in r:
                cuisines.add(r['cuisine'])
            if 'tags' in r:
                tags.update(r['tags'])

        return render_template('browse.html', recipes=filtered, cuisines=sorted(cuisines), tags=sorted(tags),
                               current_filter=filter_type, current_value=filter_value)

    @app.route('/add_recipe', methods=['GET', 'POST'])
    def add_recipe():
        if request.method == 'POST':
            recipe_data = {
                'name': request.form.get('name', '').strip(),
                'ingredients': parse_ingredient_list(request.form.get('ingredients', '')),
                'instructions': [i.strip() for i in request.form.get('instructions', '').split('\n') if i.strip()],
                'cook_time': request.form.get('cook_time', '').strip(),
                'difficulty': request.form.get('difficulty', 'Easy'),
                'servings': int(request.form.get('servings', 1)),
                'cuisine': request.form.get('cuisine', '').strip(),
                'tags': [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
                'created_at': datetime.now().isoformat(),
                'created_by': 'user'
            }

            is_valid, errors = validate_recipe_data(recipe_data)
            if not is_valid:
                for error in errors:
                    flash(error, 'error')
                return render_template('add_recipe.html', recipe_data=recipe_data)

            base_id = ''.join(c for c in recipe_data['name'].lower().replace(' ', '_') if c.isalnum() or c == '_')
            recipe_id = base_id
            count = 1
            while recipe_assistant.database.get_recipe(recipe_id):
                recipe_id = f"{base_id}_{count}"
                count += 1

            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{recipe_id}_{file.filename}")
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(path)
                    recipe_data['image'] = filename

            if recipe_assistant.database.add_recipe(recipe_id, recipe_data):
                flash(f'Recipe "{recipe_data["name"]}" added successfully.', 'success')
                return redirect(url_for('view_recipe', recipe_id=recipe_id))
            else:
                flash('Failed to save recipe. Please try again.', 'error')

        return render_template('add_recipe.html')

    @app.route('/shopping_list')
    def shopping_list():
        recipe_ids = request.args.getlist('recipes')
        if not recipe_ids:
            flash('No recipes selected.', 'error')
            return redirect(url_for('browse_recipes'))

        shopping_items = {}
        selected = []

        for rid in recipe_ids:
            recipe = recipe_assistant.database.get_recipe(rid)
            if recipe:
                selected.append({'id': rid, 'name': recipe['name']})
                for ing in recipe['ingredients']:
                    key = ing.lower()
                    if key in shopping_items:
                        shopping_items[key]['count'] += 1
                        shopping_items[key]['recipes'].append(recipe['name'])
                    else:
                        shopping_items[key] = {'name': ing, 'count': 1, 'recipes': [recipe['name']]}

        return render_template('shopping_list.html', shopping_items=shopping_items, selected_recipes=selected)

    @app.route('/api/v1/recipes')
    def api_recipes():
        return jsonify(recipe_assistant.database.get_all_recipes())

    @app.route('/api/v1/search')
    def api_search():
        ingredients = request.args.get('ingredients', '').strip()
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400
        parsed = parse_ingredient_list(ingredients)
        matches = recipe_assistant.find_recipes_by_ingredients(parsed)
        results = [{
            'recipe_id': m['recipe_id'],
            'name': m['recipe']['name'],
            'match_percentage': round(m['match_percentage'], 1),
            'cook_time': m['recipe']['cook_time'],
            'difficulty': m['recipe']['difficulty'],
            'missing_ingredients': m['missing_ingredients']
        } for m in matches if m['match_percentage'] >= 20]
        return jsonify(results)

    @app.route('/meal_planner')
    def meal_planner():
        return render_template('meal_planner.html')

    @app.route('/favorites')
    def favorites():
        ids = session.get('favorites', [])
        recipes = {rid: recipe_assistant.database.get_recipe(rid)
                   for rid in ids if recipe_assistant.database.get_recipe(rid)}
        return render_template('favorites.html', recipes=recipes)

    @app.route('/toggle_favorite/<recipe_id>')
    def toggle_favorite(recipe_id):
        favorites = session.get('favorites', [])
        if recipe_id in favorites:
            favorites.remove(recipe_id)
            action = 'removed from'
        else:
            favorites.append(recipe_id)
            action = 'added to'
        session['favorites'] = favorites
        flash(f'Recipe {action} favorites.', 'success')
        return redirect(request.referrer or url_for('view_recipe', recipe_id=recipe_id))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0', port=5000)
