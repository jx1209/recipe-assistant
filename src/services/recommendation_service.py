"""
recipe recommendation service
provides intelligent recipe recommendations based on various factors
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class RecommendationService:
    """manages recipe recommendations"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
    
    async def get_recommendations_for_user(
        self,
        user_id: int,
        limit: int = 10,
        exclude_viewed: bool = False
    ) -> List[Dict]:
        """
        get personalized recipe recommendations for user
        based on favorites, ratings, and dietary preferences
        """
        try:
            cursor = self.conn.cursor()
            
            #get user preferences
            cursor.execute("""
                SELECT dietary_restrictions, allergies, favorite_cuisines
                FROM users
                WHERE id = ?
            """, (user_id,))
            user_row = cursor.fetchone()
            
            dietary_restrictions = []
            allergies = []
            favorite_cuisines = []
            
            if user_row:
                dietary_restrictions = json.loads(user_row['dietary_restrictions'] or '[]')
                allergies = json.loads(user_row['allergies'] or '[]')
                favorite_cuisines = json.loads(user_row['favorite_cuisines'] or '[]')
            
            #get user's favorite recipes to analyze patterns
            cursor.execute("""
                SELECT r.* FROM recipes r
                INNER JOIN user_favorites uf ON r.id = uf.recipe_id
                WHERE uf.user_id = ? AND r.is_deleted = 0
                LIMIT 20
            """, (user_id,))
            
            favorite_recipes = cursor.fetchall()
            
            #analyze patterns from favorites
            favorite_tags = []
            favorite_cuisines_from_favorites = []
            
            for recipe in favorite_recipes:
                cursor.execute("""
                    SELECT tag_name FROM recipe_tags WHERE recipe_id = ?
                """, (recipe['id'],))
                favorite_tags.extend([row[0] for row in cursor.fetchall()])
                
                if recipe['cuisine']:
                    favorite_cuisines_from_favorites.append(recipe['cuisine'])
            
            #combine with user preferences
            all_favorite_cuisines = favorite_cuisines + favorite_cuisines_from_favorites
            cuisine_counts = Counter(all_favorite_cuisines)
            tag_counts = Counter(favorite_tags)
            
            #build recommendation query
            where_clauses = ["r.is_deleted = 0"]
            params = []
            
            #exclude already favorited
            where_clauses.append("""
                r.id NOT IN (
                    SELECT recipe_id FROM user_favorites WHERE user_id = ?
                )
            """)
            params.append(user_id)
            
            #exclude viewed if requested
            if exclude_viewed:
                pass  #future: track viewed recipes
            
            #exclude allergens
            for allergen in allergies:
                where_clauses.append("LOWER(r.ingredients_json) NOT LIKE ?")
                params.append(f"%{allergen.lower()}%")
            
            where_sql = " AND ".join(where_clauses)
            
            #get candidates
            query = f"""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
                FROM recipes r
                WHERE {where_sql}
                AND (
                    SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id
                ) >= 3.5
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT ?
            """
            
            params.append(limit * 3)  #get more candidates to score
            cursor.execute(query, params)
            candidates = cursor.fetchall()
            
            #score each candidate
            scored_recipes = []
            for recipe in candidates:
                score = 0
                
                #base rating score
                if recipe['avg_rating']:
                    score += recipe['avg_rating'] * 20
                
                #rating count (popularity)
                score += min(recipe['rating_count'] * 2, 20)
                
                #cuisine match
                if recipe['cuisine']:
                    cuisine_score = cuisine_counts.get(recipe['cuisine'], 0)
                    score += min(cuisine_score * 5, 30)
                
                #tag match
                cursor.execute("""
                    SELECT tag_name FROM recipe_tags WHERE recipe_id = ?
                """, (recipe['id'],))
                recipe_tags = [row[0] for row in cursor.fetchall()]
                
                for tag in recipe_tags:
                    tag_score = tag_counts.get(tag, 0)
                    score += min(tag_score * 3, 20)
                
                scored_recipes.append({
                    'recipe': recipe,
                    'score': score
                })
            
            #sort by score and return top recommendations
            scored_recipes.sort(key=lambda x: x['score'], reverse=True)
            
            recommendations = []
            for item in scored_recipes[:limit]:
                recipe = item['recipe']
                recommendations.append({
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'description': recipe['description'],
                    'image_url': recipe['image_url'],
                    'cuisine': recipe['cuisine'],
                    'difficulty': recipe['difficulty'],
                    'total_time_minutes': recipe['total_time_minutes'],
                    'average_rating': round(recipe['avg_rating'], 2) if recipe['avg_rating'] else None,
                    'rating_count': recipe['rating_count'],
                    'recommendation_score': round(item['score'], 1)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"error getting recommendations for user {user_id}: {e}")
            raise
    
    async def get_similar_recipes(
        self,
        recipe_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        find recipes similar to the given recipe
        based on cuisine, tags, ingredients, and difficulty
        """
        try:
            cursor = self.conn.cursor()
            
            #get source recipe
            cursor.execute("""
                SELECT * FROM recipes WHERE id = ? AND is_deleted = 0
            """, (recipe_id,))
            source_recipe = cursor.fetchone()
            
            if not source_recipe:
                return []
            
            #get source recipe tags
            cursor.execute("""
                SELECT tag_name FROM recipe_tags WHERE recipe_id = ?
            """, (recipe_id,))
            source_tags = set(row[0] for row in cursor.fetchall())
            
            #parse source ingredients
            source_ingredients = json.loads(source_recipe['ingredients_json'])
            source_ingredient_names = set(ing['name'].lower() for ing in source_ingredients)
            
            #find candidates
            cursor.execute("""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
                FROM recipes r
                WHERE r.is_deleted = 0 AND r.id != ?
                LIMIT 200
            """, (recipe_id,))
            candidates = cursor.fetchall()
            
            #score candidates
            scored_recipes = []
            for candidate in candidates:
                score = 0
                
                #same cuisine
                if candidate['cuisine'] and candidate['cuisine'] == source_recipe['cuisine']:
                    score += 40
                
                #same difficulty
                if candidate['difficulty'] == source_recipe['difficulty']:
                    score += 10
                
                #similar cooking time
                if source_recipe['total_time_minutes'] and candidate['total_time_minutes']:
                    time_diff = abs(source_recipe['total_time_minutes'] - candidate['total_time_minutes'])
                    if time_diff < 15:
                        score += 20
                    elif time_diff < 30:
                        score += 10
                    elif time_diff < 60:
                        score += 5
                
                #shared tags
                cursor.execute("""
                    SELECT tag_name FROM recipe_tags WHERE recipe_id = ?
                """, (candidate['id'],))
                candidate_tags = set(row[0] for row in cursor.fetchall())
                
                shared_tags = source_tags.intersection(candidate_tags)
                score += len(shared_tags) * 15
                
                #shared ingredients
                candidate_ingredients = json.loads(candidate['ingredients_json'])
                candidate_ingredient_names = set(ing['name'].lower() for ing in candidate_ingredients)
                
                shared_ingredients = source_ingredient_names.intersection(candidate_ingredient_names)
                score += len(shared_ingredients) * 5
                
                #rating bonus
                if candidate['avg_rating']:
                    score += candidate['avg_rating'] * 3
                
                scored_recipes.append({
                    'recipe': candidate,
                    'score': score
                })
            
            #sort and return top results
            scored_recipes.sort(key=lambda x: x['score'], reverse=True)
            
            recommendations = []
            for item in scored_recipes[:limit]:
                recipe = item['recipe']
                recommendations.append({
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'description': recipe['description'],
                    'image_url': recipe['image_url'],
                    'cuisine': recipe['cuisine'],
                    'difficulty': recipe['difficulty'],
                    'total_time_minutes': recipe['total_time_minutes'],
                    'average_rating': round(recipe['avg_rating'], 2) if recipe['avg_rating'] else None,
                    'rating_count': recipe['rating_count'],
                    'similarity_score': round(item['score'], 1)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"error getting similar recipes for {recipe_id}: {e}")
            raise
    
    async def get_recommendations_by_ingredients(
        self,
        ingredients: List[str],
        limit: int = 10
    ) -> List[Dict]:
        """
        recommend recipes based on available ingredients
        prioritizes recipes that use most of the provided ingredients
        """
        try:
            cursor = self.conn.cursor()
            
            #normalize ingredient names
            ingredients_lower = [ing.lower().strip() for ing in ingredients]
            
            #get all recipes
            cursor.execute("""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count
                FROM recipes r
                WHERE r.is_deleted = 0
                LIMIT 500
            """)
            candidates = cursor.fetchall()
            
            #score based on ingredient matches
            scored_recipes = []
            for recipe in candidates:
                recipe_ingredients = json.loads(recipe['ingredients_json'])
                recipe_ingredient_names = [ing['name'].lower() for ing in recipe_ingredients]
                
                #count matches
                matches = sum(1 for ing in recipe_ingredient_names 
                            if any(provided in ing or ing in provided 
                                   for provided in ingredients_lower))
                
                if matches == 0:
                    continue  #skip recipes with no ingredient matches
                
                #calculate score
                match_percentage = (matches / len(recipe_ingredient_names)) * 100
                score = match_percentage * 2
                
                #add rating bonus
                if recipe['avg_rating']:
                    score += recipe['avg_rating'] * 5
                
                scored_recipes.append({
                    'recipe': recipe,
                    'score': score,
                    'matches': matches,
                    'total_ingredients': len(recipe_ingredient_names),
                    'match_percentage': round(match_percentage, 1)
                })
            
            #sort by score
            scored_recipes.sort(key=lambda x: (x['score'], x['matches']), reverse=True)
            
            recommendations = []
            for item in scored_recipes[:limit]:
                recipe = item['recipe']
                recommendations.append({
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'description': recipe['description'],
                    'image_url': recipe['image_url'],
                    'cuisine': recipe['cuisine'],
                    'difficulty': recipe['difficulty'],
                    'total_time_minutes': recipe['total_time_minutes'],
                    'average_rating': round(recipe['avg_rating'], 2) if recipe['avg_rating'] else None,
                    'rating_count': recipe['rating_count'],
                    'matched_ingredients': item['matches'],
                    'total_ingredients': item['total_ingredients'],
                    'match_percentage': item['match_percentage']
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"error getting recommendations by ingredients: {e}")
            raise
    
    async def get_trending_recipes(
        self,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """
        get trending recipes based on recent views, favorites, and ratings
        """
        try:
            cursor = self.conn.cursor()
            
            #get recipes with recent activity
            #note: this is simplified - in production you'd track views with timestamps
            cursor.execute("""
                SELECT r.*,
                    (SELECT AVG(rating) FROM recipe_ratings WHERE recipe_id = r.id) as avg_rating,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) as rating_count,
                    (SELECT COUNT(*) FROM user_favorites WHERE recipe_id = r.id) as favorite_count
                FROM recipes r
                WHERE r.is_deleted = 0
                ORDER BY 
                    rating_count DESC,
                    favorite_count DESC,
                    r.view_count DESC
                LIMIT ?
            """, (limit,))
            
            recipes = cursor.fetchall()
            
            trending = []
            for recipe in recipes:
                trending.append({
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'description': recipe['description'],
                    'image_url': recipe['image_url'],
                    'cuisine': recipe['cuisine'],
                    'difficulty': recipe['difficulty'],
                    'total_time_minutes': recipe['total_time_minutes'],
                    'average_rating': round(recipe['avg_rating'], 2) if recipe['avg_rating'] else None,
                    'rating_count': recipe['rating_count'],
                    'favorite_count': recipe['favorite_count'],
                    'view_count': recipe['view_count']
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"error getting trending recipes: {e}")
            raise

