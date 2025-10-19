<!-- 4a197afe-53d9-4ea5-8297-e6932afa587b ad58c459-5342-4d17-9e7f-9dfde3ad1f49 -->
# Recipe Assistant - Full Production Build Plan

## Architecture Overview

**Technology Stack:**

- **Backend:** FastAPI + SQLite (JWT authentication)
- **Web Frontend:** Next.js 14 (React, TypeScript, Tailwind CSS)
- **Desktop App:** Electron (bundles Next.js UI + Python backend)
- **AI Integration:** Claude API (optional, user-provided key) + rule-based fallbacks
- **Recipe Scraping:** recipe-scrapers library
- **Deployment:** Docker containers for web, packaged installers for desktop

---

## Phase 1: Database & Core Backend Setup

### 1.1 Database Schema Design

**File:** `src/database/schema.sql`

Design comprehensive SQLite schema:

- **users** table (id, email, password_hash, created_at, preferences_json)
- **recipes** table (id, title, source_url, ingredients_json, instructions_json, nutrition_json, image_url, created_by, created_at, updated_at)
- **user_favorites** table (user_id, recipe_id, added_at)
- **meal_plans** table (id, user_id, start_date, end_date, meals_json, created_at)
- **shopping_lists** table (id, user_id, items_json, checked_items_json, created_at)
- **recipe_ratings** table (id, recipe_id, user_id, rating, review, created_at)
- **user_pantry** table (user_id, ingredient_name, quantity, unit, added_at)
- **recipe_tags** table (recipe_id, tag_name)
- **user_dietary_restrictions** table (user_id, restriction_type)

### 1.2 Database Management Module

**File:** `src/database/db_manager.py`

Create comprehensive database manager:

- Connection pooling
- Migration system (Alembic integration)
- CRUD operations for all tables
- Transaction management
- Backup/restore functionality
- Index optimization

### 1.3 Models & Schemas

**File:** `src/models/`

Create Pydantic models for:

- User (UserCreate, UserLogin, UserProfile, UserUpdate)
- Recipe (RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSearch)
- MealPlan (MealPlanCreate, MealPlanResponse)
- ShoppingList (ShoppingListCreate, ShoppingListResponse)
- Nutrition (NutritionInfo, NutritionAnalysis)

---

## Phase 2: Authentication & User Management

### 2.1 Authentication System

**File:** `src/auth/auth_handler.py`

Implement JWT-based authentication:

- Password hashing (bcrypt)
- JWT token generation/validation
- Refresh token mechanism
- Token blacklist for logout
- Password reset functionality (email integration optional)

### 2.2 User Management API

**File:** `src/api/routes/users.py`

Create FastAPI routes:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate token
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `PUT /api/users/me/preferences` - Update dietary preferences
- `GET /api/users/me/pantry` - Get user pantry items
- `POST /api/users/me/pantry` - Add pantry item

### 2.3 Middleware & Dependencies

**File:** `src/api/middleware.py`

Create:

- Authentication middleware (verify JWT)
- Rate limiting middleware
- CORS configuration
- Error handling middleware
- Request logging middleware

---

## Phase 3: Recipe Management System

### 3.1 Recipe Import/Scraping

**File:** `src/recipe_importer/scraper.py`

Enhance existing importer:

- Integrate recipe-scrapers for 100+ websites
- Handle various URL formats
- Extract: title, ingredients, instructions, nutrition, images, cook time, servings
- Validate scraped data
- Store source attribution
- Handle scraping errors gracefully

**File:** `src/recipe_importer/manual_parser.py`

Text parsing for manual recipe entry:

- Parse free-form text recipes
- Extract structured data using regex + NLP
- Handle various recipe formats
- Ingredient parsing (quantity, unit, name)

### 3.2 Recipe CRUD API

**File:** `src/api/routes/recipes.py`

Create comprehensive recipe endpoints:

- `POST /api/recipes/import/url` - Import from URL
- `POST /api/recipes/import/text` - Import from text
- `POST /api/recipes` - Create recipe manually
- `GET /api/recipes/{id}` - Get recipe by ID
- `PUT /api/recipes/{id}` - Update recipe
- `DELETE /api/recipes/{id}` - Delete recipe (soft delete)
- `GET /api/recipes` - List recipes (pagination, filters)
- `POST /api/recipes/{id}/favorite` - Add to favorites
- `DELETE /api/recipes/{id}/favorite` - Remove from favorites
- `GET /api/recipes/favorites` - Get user favorites
- `POST /api/recipes/{id}/rate` - Rate recipe
- `GET /api/recipes/{id}/ratings` - Get recipe ratings

### 3.3 Recipe Search Engine

**File:** `src/search/advanced_search.py`

Rebuild search with:

- Full-text search (FTS5 extension)
- Fuzzy matching for ingredients
- Filter by: cuisine, tags, cook time, difficulty, dietary restrictions
- Sort by: relevance, rating, cook time, date added
- Ingredient-based matching (what you have vs. what you need)
- Pagination and result caching

---

## Phase 4: Core Features Implementation

### 4.1 Meal Planning System

**File:** `src/core/meal_planner_v2.py`

Refactor existing meal planner:

- Generate weekly/monthly meal plans
- Consider user preferences and dietary restrictions
- Balance nutrition across days
- Minimize ingredient waste
- Support user-defined meals
- Calendar integration
- Export to PDF/iCal

**API Routes:** `src/api/routes/meal_plans.py`

- `POST /api/meal-plans/generate` - AI-powered meal plan generation
- `GET /api/meal-plans` - List user meal plans
- `GET /api/meal-plans/{id}` - Get specific plan
- `PUT /api/meal-plans/{id}` - Update meal plan
- `DELETE /api/meal-plans/{id}` - Delete meal plan

### 4.2 Shopping List Generator

**File:** `src/core/shopping_list_v2.py`

Enhanced shopping list:

- Generate from meal plans or selected recipes
- Categorize by grocery aisle
- Check against user pantry
- Combine duplicate ingredients
- Unit conversion and normalization
- Export formats: PDF, text, mobile app integration

**API Routes:** `src/api/routes/shopping_lists.py`

- `POST /api/shopping-lists/generate` - Generate from recipes/meal plans
- `GET /api/shopping-lists/{id}` - Get shopping list
- `PUT /api/shopping-lists/{id}/check` - Mark items as purchased
- `DELETE /api/shopping-lists/{id}` - Delete list

### 4.3 Nutrition Calculator

**File:** `src/core/nutrition_calculator_v2.py`

Integrate with existing calculator:

- Calculate per-serving nutrition
- USDA nutrition database integration (optional)
- Nutrition scoring system
- Dietary compliance checking
- Daily nutrition tracking
- Nutrition goals and progress

**API Routes:** `src/api/routes/nutrition.py`

- `GET /api/recipes/{id}/nutrition` - Get recipe nutrition
- `POST /api/nutrition/analyze` - Analyze custom meal
- `GET /api/nutrition/daily/{date}` - Get daily nutrition summary
- `POST /api/nutrition/goals` - Set nutrition goals

### 4.4 Recommendation Engine

**File:** `src/ai/recommendation_engine_v2.py`

Intelligent recommendations:

- Collaborative filtering (based on ratings)
- Content-based filtering (similar recipes)
- User preference learning
- Trending recipes
- Seasonal recommendations
- "You might also like" suggestions

**API Routes:** `src/api/routes/recommendations.py`

- `GET /api/recommendations/personalized` - Personalized recommendations
- `GET /api/recommendations/similar/{recipe_id}` - Similar recipes
- `GET /api/recommendations/trending` - Trending recipes

### 4.5 Ingredient Substitution

**File:** `src/core/substitution_engine_v2.py`

Enhanced substitution engine:

- Dietary-based substitutions (vegan, gluten-free, etc.)
- Allergy-safe alternatives
- Availability-based suggestions
- Nutritionally similar alternatives
- AI-powered substitution suggestions (Claude API)

**API Routes:** `src/api/routes/substitutions.py`

- `POST /api/substitutions/suggest` - Get substitution suggestions

---

## Phase 5: AI Integration (Optional/Premium)

### 5.1 Claude API Integration

**File:** `src/ai/claude_integration.py`

Implement Claude API features:

- Recipe generation from ingredients
- Smart recipe modifications
- Cooking questions Q&A
- Recipe translation/adaptation
- Nutrition insights
- User-provided API key management
- Fallback to rule-based when no API key

**API Routes:** `src/api/routes/ai.py`

- `POST /api/ai/generate-recipe` - Generate recipe from prompt
- `POST /api/ai/modify-recipe` - Modify existing recipe
- `POST /api/ai/cooking-help` - Ask cooking questions
- `POST /api/ai/api-key` - Set user's Claude API key (encrypted storage)

### 5.2 Rule-Based Fallbacks

**File:** `src/ai/rule_based_ai.py`

Implement non-AI alternatives:

- Template-based recipe generation
- Ingredient combination rules
- Basic cooking tips database
- Pre-generated meal plan templates

---

## Phase 6: Backend API Consolidation

### 6.1 Main FastAPI Application

**File:** `src/api/main_v2.py`

Rebuild main API:

- Clean architecture (routers, dependencies, middleware)
- API documentation (Swagger/OpenAPI)
- Health check endpoint
- Version prefix (`/api/v1/`)
- WebSocket support for real-time updates
- Background task queue (for slow operations)

### 6.2 Configuration Management

**File:** `src/config/settings.py`

Environment-based configuration:

- Development, staging, production configs
- Database URLs
- JWT secret keys
- CORS origins
- API rate limits
- File upload limits
- Claude API settings

### 6.3 Testing Suite

**Files:** `tests/`

Comprehensive testing:

- Unit tests for all modules
- Integration tests for API endpoints
- Database tests
- Authentication tests
- Mock external services (recipe scraping, AI)
- Load testing for scalability

---

## Phase 7: Web Frontend (Next.js)

### 7.1 Project Setup

**Directory:** `frontend/`

Initialize Next.js 14:

- TypeScript configuration
- Tailwind CSS setup
- shadcn/ui component library
- React Query for API calls
- Zustand for state management
- next-auth for authentication
- Environment variables setup

### 7.2 Authentication UI

**Files:** `frontend/app/(auth)/`

Create auth pages:

- `/login` - Login page with form validation
- `/register` - Registration page
- `/forgot-password` - Password reset
- Protected route wrapper
- Token management (localStorage/cookies)
- Auto-refresh tokens

### 7.3 Main Application Pages

**Dashboard:** `frontend/app/dashboard/page.tsx`

- Welcome message
- Recent recipes
- Today's meal plan
- Quick actions (search, import, plan)
- Nutrition summary

**Recipe Search:** `frontend/app/recipes/page.tsx`

- Search bar with filters
- Recipe grid with cards
- Infinite scroll/pagination
- Filter sidebar (cuisine, tags, time, difficulty)
- Sort options

**Recipe Detail:** `frontend/app/recipes/[id]/page.tsx`

- Recipe header with image
- Ingredients list (with pantry check)
- Step-by-step instructions
- Nutrition facts
- Rating/reviews
- Save to favorites
- Add to meal plan
- Share button

**Recipe Import:** `frontend/app/recipes/import/page.tsx`

- URL import form
- Text paste area
- PDF upload (future)
- Preview imported recipe
- Edit before saving

**Meal Planner:** `frontend/app/meal-planner/page.tsx`

- Weekly calendar view
- Drag-and-drop recipes to days
- Generate AI meal plan button
- Nutrition overview for week
- Export shopping list button
- Print meal plan

**Shopping List:** `frontend/app/shopping-list/page.tsx`

- Categorized ingredient list
- Check off items
- Edit quantities
- Print/export options
- Share with others

**Pantry:** `frontend/app/pantry/page.tsx`

- Ingredient inventory
- Add/remove items
- Expiration tracking
- Low stock alerts
- Suggest recipes based on pantry

**Profile:** `frontend/app/profile/page.tsx`

- User information
- Dietary preferences
- Allergies/restrictions
- Nutrition goals
- API key management (Claude)
- Export user data

### 7.4 Component Library

**Files:** `frontend/components/`

Reusable components:

- `RecipeCard` - Recipe preview card
- `SearchBar` - Search with autocomplete
- `IngredientList` - Interactive ingredient list
- `NutritionLabel` - FDA-style nutrition facts
- `MealPlanCalendar` - Calendar with meals
- `LoadingSpinner`, `ErrorBoundary`, etc.

### 7.5 API Integration Layer

**File:** `frontend/lib/api.ts`

API client:

- Axios/Fetch wrapper
- Request/response interceptors
- Error handling
- Token refresh logic
- Type-safe API calls

---

## Phase 8: Desktop Application (Electron)

### 8.1 Electron Setup

**Directory:** `desktop/`

Initialize Electron app:

- Main process setup (`main.js`)
- Bundle Next.js production build
- Bundle Python FastAPI backend (PyInstaller)
- IPC communication between frontend and backend
- Local SQLite database
- Auto-update mechanism

### 8.2 Desktop-Specific Features

**File:** `desktop/preload.js`

Desktop capabilities:

- File system access (import recipes from files)
- System tray integration
- Native notifications
- Offline mode support
- Local recipe backup
- Print functionality

### 8.3 Packaging & Distribution

**Files:** `desktop/package.json`, `desktop/electron-builder.yml`

Create installers:

- Windows (.exe, .msi)
- macOS (.dmg, .app)
- Linux (.deb, .AppImage)
- Code signing
- Auto-update configuration

---

## Phase 9: Deployment & Infrastructure

### 9.1 Docker Configuration

**Files:** `Dockerfile`, `docker-compose.yml`

Containerize application:

- FastAPI backend container
- Next.js frontend container (if self-hosting)
- Nginx reverse proxy
- SQLite volume mounting
- Environment variable management

### 9.2 Web Deployment

**Backend Options:**

- Railway, Render, or DigitalOcean App Platform
- Environment variables configuration
- Database backup strategy
- Monitoring and logging

**Frontend Options:**

- Vercel (recommended for Next.js)
- Netlify
- Environment variables for API endpoint

### 9.3 CI/CD Pipeline

**File:** `.github/workflows/`

Automated workflows:

- Test on push
- Build and deploy backend
- Build and deploy frontend
- Build desktop installers
- Release management

---

## Phase 10: Documentation & Polish

### 10.1 API Documentation

**File:** `docs/api.md`

Comprehensive API docs:

- Automatically generated from FastAPI (Swagger)
- Authentication guide
- Example requests/responses
- Rate limiting information
- Error codes reference

### 10.2 User Documentation

**Files:** `docs/user-guide.md`, `README.md`

User-facing documentation:

- Installation guide (web and desktop)
- Quick start tutorial
- Feature walkthroughs
- FAQ
- Troubleshooting

### 10.3 Developer Documentation

**File:** `docs/development.md`

Developer guide:

- Architecture overview
- Setup instructions
- Code style guide
- Contributing guidelines
- Database schema reference

### 10.4 Final Polish

Quality assurance:

- UI/UX review and improvements
- Performance optimization
- Security audit
- Accessibility compliance (WCAG)
- Mobile responsiveness testing
- Cross-browser testing
- Load testing and optimization

---

## Phase 11: Sample Data & Seeding

### 11.1 Recipe Dataset

**File:** `data/seed_recipes.json`

Create/import initial recipes:

- 100+ sample recipes across cuisines
- Properly formatted with all fields
- Include images (or placeholder URLs)
- Diverse difficulty levels
- Complete nutrition data

### 11.2 Database Seeding

**File:** `src/database/seed.py`

Seeding script:

- Import sample recipes
- Create demo user accounts
- Generate sample meal plans
- Populate tags and categories
- Add sample ratings

---

## Success Metrics

**Functionality Checklist:**

- ✅ User registration and authentication working
- ✅ Recipe import from 50+ websites
- ✅ Advanced recipe search with filters
- ✅ Meal plan generation (7-day plans)
- ✅ Shopping list generation from meal plans
- ✅ Nutrition calculation and tracking
- ✅ User pantry management
- ✅ Favorites and ratings system
- ✅ Desktop app launches and works offline
- ✅ Web app deployed and accessible
- ✅ Mobile-responsive design
- ✅ AI features (optional with API key)

**Performance Targets:**

- API response time < 200ms (avg)
- Recipe search < 100ms
- Support 1000+ concurrent users (web)
- Desktop app < 500MB installed
- Page load time < 2 seconds

**Security Requirements:**

- Password hashing (bcrypt)
- JWT token authentication
- SQL injection prevention
- XSS protection
- HTTPS/TLS encryption
- Rate limiting on endpoints

### To-dos

- [ ] Database & Core Backend - Design schema, implement db_manager.py, create Pydantic models
- [ ] Authentication System - Implement JWT auth, user management API, middleware
- [ ] Recipe Management - Build scraper, CRUD API, advanced search engine
- [ ] Core Features - Meal planner, shopping lists, nutrition calculator, recommendations, substitutions
- [ ] AI Integration - Claude API wrapper, rule-based fallbacks, AI endpoints
- [ ] API Consolidation - Main FastAPI app, config management, comprehensive testing
- [ ] Web Frontend - Next.js setup, all pages, components, API integration
- [ ] Desktop Application - Electron setup, packaging, installers
- [ ] Deployment - Docker setup, web deployment, CI/CD pipeline
- [ ] Documentation & Polish - API docs, user guide, final QA and optimization
- [ ] Sample Data - Create recipe dataset, seeding scripts, demo content