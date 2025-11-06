# Grocery List MVP 🛒

Zero-friction grocery list management. Add items, check them off, repeat.

## Features

- **Instant item entry**: Add items by name
- **Toggle bought status**: Check off items as you shop
- **Persistent items**: Items stay in your list for re-use
- **Secure**: Supabase auth with RLS

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + Auth)
- **Deploy**: Vercel

## Setup

### 1. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the migration:
   ```sql
   -- Copy contents from migrations/init.sql
   ```
3. Get your credentials from **Project Settings > API**:
   - Project URL → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_KEY`

### 2. Local Development

```bash
# Clone and install
cd grocery-list-mvp
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run locally
uvicorn api.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# SUPABASE_URL
# SUPABASE_KEY
```

## API Endpoints

### Authentication
All endpoints require `Authorization: Bearer <jwt_token>` header.
Get token from Supabase Auth SDK in your frontend.

### Endpoints

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

## Frontend Integration

```javascript
// Example: Add item
const response = await fetch('https://your-api.vercel.app/api/items', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${supabaseToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ name: 'Eggs' })
});
```

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

- Row Level Security (RLS) enforced
- Users can only access their own items
- JWT authentication via Supabase
