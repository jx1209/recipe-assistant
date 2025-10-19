-- Recipe Assistant Database Schema
-- SQLite Database Schema for Production Application
-- Version: 1.0.0

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    preferences_json TEXT DEFAULT '{}',
    -- Preferences includes: dietary restrictions, allergies, favorite cuisines, etc.
    CONSTRAINT email_format CHECK (email LIKE '%_@__%.__%')
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    source_name TEXT,
    ingredients_json TEXT NOT NULL, -- JSON array of ingredients with quantities
    instructions_json TEXT NOT NULL, -- JSON array of instruction steps
    nutrition_json TEXT, -- JSON object with nutrition info
    image_url TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    total_time_minutes INTEGER,
    servings INTEGER DEFAULT 1,
    difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')),
    cuisine TEXT,
    created_by INTEGER, -- User ID who created/imported
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0, -- Soft delete
    view_count INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title);
CREATE INDEX IF NOT EXISTS idx_recipes_cuisine ON recipes(cuisine);
CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX IF NOT EXISTS idx_recipes_created_by ON recipes(created_by);
CREATE INDEX IF NOT EXISTS idx_recipes_created_at ON recipes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_deleted ON recipes(is_deleted);
CREATE INDEX IF NOT EXISTS idx_recipes_total_time ON recipes(total_time_minutes);

-- Full-text search index for recipes
CREATE VIRTUAL TABLE IF NOT EXISTS recipes_fts USING fts5(
    title,
    description,
    cuisine,
    content='recipes',
    content_rowid='id'
);

-- Triggers to keep FTS in sync with recipes
CREATE TRIGGER IF NOT EXISTS recipes_ai AFTER INSERT ON recipes BEGIN
    INSERT INTO recipes_fts(rowid, title, description, cuisine)
    VALUES (new.id, new.title, new.description, new.cuisine);
END;

CREATE TRIGGER IF NOT EXISTS recipes_ad AFTER DELETE ON recipes BEGIN
    DELETE FROM recipes_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS recipes_au AFTER UPDATE ON recipes BEGIN
    UPDATE recipes_fts 
    SET title = new.title, 
        description = new.description,
        cuisine = new.cuisine
    WHERE rowid = new.id;
END;

-- Recipe tags (for categorization and filtering)
CREATE TABLE IF NOT EXISTS recipe_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    UNIQUE(recipe_id, tag_name)
);

CREATE INDEX IF NOT EXISTS idx_recipe_tags_recipe ON recipe_tags(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_tags_tag ON recipe_tags(tag_name);

-- User favorites
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    UNIQUE(user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_recipe ON user_favorites(recipe_id);

-- Recipe ratings and reviews
CREATE TABLE IF NOT EXISTS recipe_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(recipe_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_ratings_recipe ON recipe_ratings(recipe_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON recipe_ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_rating ON recipe_ratings(rating);

-- User pantry
CREATE TABLE IF NOT EXISTS user_pantry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
    expiration_date DATE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pantry_user ON user_pantry(user_id);
CREATE INDEX IF NOT EXISTS idx_pantry_ingredient ON user_pantry(ingredient_name);
CREATE INDEX IF NOT EXISTS idx_pantry_expiration ON user_pantry(expiration_date);

-- Meal plans
CREATE TABLE IF NOT EXISTS meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_name TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    meals_json TEXT NOT NULL, -- JSON with structure: {date: {breakfast: recipe_id, lunch: recipe_id, dinner: recipe_id}}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_meal_plans_user ON meal_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_dates ON meal_plans(start_date, end_date);

-- Shopping lists
CREATE TABLE IF NOT EXISTS shopping_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    list_name TEXT,
    items_json TEXT NOT NULL, -- JSON array of shopping items
    meal_plan_id INTEGER, -- Optional link to meal plan
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_shopping_lists_user ON shopping_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_shopping_lists_meal_plan ON shopping_lists(meal_plan_id);

-- User dietary restrictions
CREATE TABLE IF NOT EXISTS user_dietary_restrictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    restriction_type TEXT NOT NULL, -- e.g., 'vegetarian', 'vegan', 'gluten-free', 'dairy-free'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, restriction_type)
);

CREATE INDEX IF NOT EXISTS idx_dietary_restrictions_user ON user_dietary_restrictions(user_id);

-- API keys (encrypted storage for user's Claude API key)
CREATE TABLE IF NOT EXISTS user_api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_name TEXT NOT NULL, -- 'anthropic', 'openai', etc.
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, service_name)
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user ON user_api_keys(user_id);

-- JWT token blacklist (for logout)
CREATE TABLE IF NOT EXISTS token_blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_jti TEXT UNIQUE NOT NULL, -- JWT ID claim
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist(token_jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires ON token_blacklist(expires_at);

-- User activity log (for analytics and debugging)
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity_type TEXT NOT NULL, -- 'login', 'logout', 'recipe_view', 'recipe_create', etc.
    activity_data_json TEXT, -- Additional context
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_type ON user_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_created ON user_activity(created_at DESC);

-- Recipe collections (user-created collections of recipes)
CREATE TABLE IF NOT EXISTS recipe_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    collection_name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_collections_user ON recipe_collections(user_id);
CREATE INDEX IF NOT EXISTS idx_collections_public ON recipe_collections(is_public);

-- Recipe collection items (many-to-many)
CREATE TABLE IF NOT EXISTS recipe_collection_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES recipe_collections(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    UNIQUE(collection_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_collection_items_collection ON recipe_collection_items(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_items_recipe ON recipe_collection_items(recipe_id);

-- Nutrition goals
CREATE TABLE IF NOT EXISTS user_nutrition_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    daily_calories INTEGER,
    daily_protein_g REAL,
    daily_carbs_g REAL,
    daily_fat_g REAL,
    daily_fiber_g REAL,
    daily_sodium_mg REAL,
    goal_type TEXT, -- 'weight_loss', 'muscle_gain', 'maintenance', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_nutrition_goals_user ON user_nutrition_goals(user_id);

-- Database metadata and migrations
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial migration
INSERT OR IGNORE INTO schema_migrations (version, description) 
VALUES ('1.0.0', 'Initial schema - Phase 1 & 2');

