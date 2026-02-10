# quick setup guide 🚀

follow these steps to get your recipe assistant up and running

## step 1: backend setup

```bash
# create and activate virtual environment
python -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# create your .env file from the example
cp .env.example .env

# generate secure secret keys (run this 3 times for each key)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# edit .env and replace the secret keys
nano .env  # or use your favorite editor
```

**important:** in your `.env` file, replace these values:
- `JWT_SECRET_KEY` - paste first generated key
- `SESSION_SECRET_KEY` - paste second generated key  
- `ENCRYPTION_KEY` - paste third generated key

## step 2: start the backend

```bash
# make sure you're in the project root with venv activated
python run_api.py
```

you should see:
```
INFO:     started server process
INFO:     uvicorn running on http://0.0.0.0:8000
```

test it: open http://localhost:8000/health in your browser

## step 3: frontend setup (new terminal)

```bash
# navigate to frontend directory
cd frontend

# install dependencies
npm install

# create your .env.local file
cp .env.local.example .env.local

# the default values should work for local development
# no need to edit unless you changed the backend port
```

## step 4: start the frontend

```bash
# make sure you're in the frontend directory
npm run dev
```

you should see:
```
ready - started server on 0.0.0.0:3000
```

open http://localhost:3000 in your browser! 🎉

## step 5: create your first account

1. go to http://localhost:3000
2. click "get started free" or "sign in"
3. click "sign up" to create an account
4. fill in your email and password (min 8 chars, needs uppercase, lowercase, and digit)
5. you're in! start adding recipes

## optional: enable ai features

if you want to use ai-powered recipe generation:

1. get an api key from [anthropic](https://console.anthropic.com/)
2. edit your `.env` file:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   AI_ENABLED=true
   FEATURE_AI_GENERATION=true
   ```
3. restart the backend server
4. go to the "ai features" page in the app

## troubleshooting

### backend issues

**"module not found" error:**
```bash
# make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"port already in use":**
```bash
# kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### frontend issues

**"cannot find module '@/lib/api'":**
- this should be fixed now! the file was created at `frontend/lib/api.ts`
- if still having issues, try: `rm -rf .next && npm run dev`

**"failed to fetch" errors:**
- make sure backend is running on port 8000
- check `frontend/.env.local` has correct `NEXT_PUBLIC_API_URL`

**cors errors:**
- check backend `.env` has `CORS_ORIGINS=http://localhost:3000`

## next steps

- ✅ create your first recipe manually
- ✅ import a recipe from a website (try allrecipes.com or foodnetwork.com)
- ✅ create a meal plan for the week
- ✅ generate a shopping list from your recipes
- ✅ try the ai features (if enabled)
- ✅ rate and review recipes

## useful commands

### backend
```bash
# run tests
pytest

# check code quality
black src/
flake8 src/

# view logs
tail -f logs/recipe_assistant.log
```

### frontend
```bash
# type check
npm run type-check

# lint
npm run lint

# build for production
npm run build
npm start
```

## need help?

- check the main [README.md](README.md) for full documentation
- review the api docs at http://localhost:8000/docs
- check logs in the `logs/` directory
- open an issue on github

happy cooking! 👨‍🍳👩‍🍳
