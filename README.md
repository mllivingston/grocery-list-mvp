# Grocery List MVP 🛒

Zero-friction grocery list management. Add items, check them off, repeat.

## Features

- **Instant item entry**: Add items by name with Enter key support
- **Toggle bought status**: Check off items as you shop
- **Delete items**: Remove duplicates or unwanted items
- **Persistent items**: Items stay in your list for re-use
- **Secure**: Supabase auth with RLS
- **Mobile-first**: Optimized for phones and tablets

## Architecture

- **Frontend**: Vanilla JavaScript with Supabase Auth
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + Auth)
- **Deploy**: Railway (single consolidated deployment)

## Setup

### 1. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the migration:
   ```sql
   -- Copy contents from migrations/init.sql
   ```
3. Get your credentials from **Project Settings > API**:
   - Project URL → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_ANON_KEY`

### 2. Local Development

```bash
# Clone and install
cd grocery-list-mvp
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run locally
cd api
uvicorn main:app --reload

# App available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Deploy to Railway

1. Push your code to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Set environment variables in Railway dashboard:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_ANON_KEY` - Your Supabase anon/public key
5. Railway will automatically deploy using `railway.toml` configuration

The app serves both frontend and backend from a single deployment, with the frontend available at the root (`/`) and API at `/api/*`.

## API Endpoints

### Authentication
All endpoints (except `/api/health` and `/api/config`) require `Authorization: Bearer <jwt_token>` header.
Get token from Supabase Auth SDK in your frontend.

### Endpoints

#### `GET /api/health`
Health check endpoint (no auth required)

#### `GET /api/config`
Get frontend configuration (no auth required)

**Response:**
```json
{
  "supabase_url": "https://xxx.supabase.co",
  "supabase_anon_key": "eyJ..."
}
```

#### `GET /api/items`
Get all grocery items (bought + unbought)

**Response:**
```json
[
  {
    "item_id": "uuid",
    "user_id": "uuid",
    "name": "Milk",
    "is_bought": false,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### `POST /api/items`
Create a new item

**Request:**
```json
{
  "name": "Bread"
}
```

**Response:** `201 Created` + ItemResponse

#### `PATCH /api/items/{item_id}/toggle`
Toggle bought status

**Response:** Updated ItemResponse

#### `DELETE /api/items/{item_id}`
Permanently delete item

**Response:** `204 No Content`

## Data Model

```
grocery_items
├── item_id (uuid, pk)
├── user_id (uuid, fk)
├── name (text)
├── is_bought (boolean)
└── created_at (timestamp)
```

## Security

- Row Level Security (RLS) enforced in Supabase
- Users can only access their own items
- JWT authentication via Supabase
- CORS configured for Railway deployment domain

## Environment Variables

Required environment variables (see `.env.example`):

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon/public key
- `RAILWAY_PUBLIC_DOMAIN` (optional) - Your Railway domain for CORS (auto-set by Railway)
