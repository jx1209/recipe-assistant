# recipe assistant 🍳

a comprehensive recipe management system with ai-powered features, intelligent meal planning, and smart cooking assistance.

## features

- 🔐 **user authentication** - secure registration and login
- 📖 **recipe management** - create, edit, and organize your recipes
- 🔍 **smart search** - find recipes by ingredients, tags, cuisine, and more
- 🌐 **recipe import** - import recipes from 100+ popular cooking websites
- 🤖 **ai-powered** - generate recipes, get cooking advice, and modify dishes with claude ai
- 📅 **meal planning** - plan your weekly meals effortlessly
- 🛒 **shopping lists** - automatically generate shopping lists from recipes
- ⭐ **ratings & reviews** - rate and review recipes
- 🥗 **nutrition tracking** - view nutritional information for recipes
- 💡 **recommendations** - get personalized recipe recommendations

## tech stack

### backend
- **fastapi** - modern python web framework
- **sqlite** - lightweight database
- **anthropic claude** - ai integration
- **recipe-scrapers** - import recipes from websites
- **jwt** - authentication
- **pydantic** - data validation

### frontend
- **next.js 14** - react framework
- **typescript** - type safety
- **tailwind css** - styling
- **axios** - api client
- **react hook form** - form handling
- **zustand** - state management

## prerequisites

- python 3.8+
- node.js 18+
- npm or yarn

## quick start

### 1. clone the repository

```bash
git clone <your-repo-url>
cd recipe-assistant
```

### 2. backend setup

```bash
# create virtual environment
python -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# create .env file
cp .env.example .env

# edit .env and add your configuration
# at minimum, change the secret keys!
nano .env
```

**important:** generate secure secret keys for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. initialize database

the database will be automatically created when you first run the application. migrations are applied automatically on startup.

### 4. run the backend

```bash
# development mode
python run_api.py

# or with uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

the api will be available at `http://localhost:8000`
api documentation: `http://localhost:8000/docs`

### 5. frontend setup

```bash
cd frontend

# install dependencies
npm install

# create .env.local file
cp .env.local.example .env.local

# edit if needed (default should work for local development)
nano .env.local

# run development server
npm run dev
```

the frontend will be available at `http://localhost:3000`

## configuration

### backend environment variables

see `.env.example` for all available options. key settings:

- `ENVIRONMENT` - development, staging, or production
- `DEBUG` - enable debug mode
- `DATABASE_URL` - path to sqlite database
- `JWT_SECRET_KEY` - secret for jwt tokens (change in production!)
- `ANTHROPIC_API_KEY` - claude api key (optional, for ai features)
- `AI_ENABLED` - enable/disable ai features
- `CORS_ORIGINS` - allowed frontend urls

### frontend environment variables

- `NEXT_PUBLIC_API_URL` - backend api url (default: http://localhost:8000/api/v1)

## enabling ai features

to use ai-powered features:

1. get an api key from [anthropic](https://www.anthropic.com/)
2. add to your `.env` file:
   ```bash
   ANTHROPIC_API_KEY=your-key-here
   AI_ENABLED=true
   FEATURE_AI_GENERATION=true
   ```
3. restart the backend server

## project structure

```
recipe-assistant/
├── src/                      # backend source code
│   ├── api/                  # api routes and main app
│   ├── auth/                 # authentication logic
│   ├── config/               # configuration settings
│   ├── core/                 # core business logic
│   ├── database/             # database manager and migrations
│   ├── models/               # pydantic models
│   ├── services/             # business services
│   └── utils/                # utility functions
├── frontend/                 # frontend source code
│   ├── app/                  # next.js app directory
│   ├── components/           # react components
│   ├── contexts/             # react contexts
│   ├── hooks/                # custom react hooks
│   └── lib/                  # utilities and api client
├── tests/                    # backend tests
├── data/                     # database and uploads
├── logs/                     # application logs
└── requirements.txt          # python dependencies
```

## api endpoints

### authentication
- `POST /api/v1/auth/register` - register new user
- `POST /api/v1/auth/login` - login
- `POST /api/v1/auth/refresh` - refresh access token

### recipes
- `GET /api/v1/recipes` - list recipes
- `GET /api/v1/recipes/{id}` - get recipe details
- `POST /api/v1/recipes` - create recipe
- `PUT /api/v1/recipes/{id}` - update recipe
- `DELETE /api/v1/recipes/{id}` - delete recipe
- `POST /api/v1/recipes/import` - import from url

### meal plans
- `GET /api/v1/meal-plans` - list meal plans
- `POST /api/v1/meal-plans` - create meal plan
- `POST /api/v1/meal-plans/generate` - ai-generate meal plan

### shopping lists
- `GET /api/v1/shopping-lists` - list shopping lists
- `POST /api/v1/shopping-lists` - create shopping list
- `POST /api/v1/shopping-lists/generate` - generate from recipes

### ai features
- `POST /api/v1/ai/generate-recipe` - generate recipe with ai
- `POST /api/v1/ai/ask` - ask cooking questions
- `POST /api/v1/ai/substitutions` - get ingredient substitutions

see full api documentation at `http://localhost:8000/docs` when running the backend.

## development

### running tests

```bash
# run all tests
pytest

# run with coverage
pytest --cov=src --cov-report=html

# run specific test file
pytest tests/test_auth.py
```

### code quality

```bash
# format code
black src/

# lint
flake8 src/
pylint src/

# type checking
mypy src/
```

### frontend development

```bash
cd frontend

# type check
npm run type-check

# lint
npm run lint

# build for production
npm run build
```

## deployment

### production checklist

- [ ] change all secret keys in `.env`
- [ ] set `ENVIRONMENT=production`
- [ ] set `DEBUG=false`
- [ ] configure proper cors origins
- [ ] set up ssl/https
- [ ] configure database backups
- [ ] set up monitoring and logging
- [ ] configure rate limiting
- [ ] secure api keys (use secrets manager)

### docker (coming soon)

docker support will be added in a future update.

## troubleshooting

### backend won't start
- check python version: `python --version` (should be 3.8+)
- ensure all dependencies are installed: `pip install -r requirements.txt`
- check database permissions
- review logs in `logs/` directory

### frontend won't start
- check node version: `node --version` (should be 18+)
- delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- check `.env.local` configuration
- ensure backend is running

### can't login/register
- check backend is running at the correct url
- verify cors settings in backend `.env`
- check browser console for errors
- review backend logs

### ai features not working
- verify `AI_ENABLED=true` in backend `.env`
- check api key is valid
- ensure you have api credits remaining
- check backend logs for errors

## contributing

contributions are welcome! please:

1. fork the repository
2. create a feature branch
3. make your changes
4. add tests if applicable
5. ensure all tests pass
6. submit a pull request

## license

this project is licensed under the mit license.

## support

for issues, questions, or suggestions, please open an issue on github.

## acknowledgments

- [anthropic claude](https://www.anthropic.com/) - ai integration
- [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) - recipe import
- [fastapi](https://fastapi.tiangolo.com/) - web framework
- [next.js](https://nextjs.org/) - frontend framework
