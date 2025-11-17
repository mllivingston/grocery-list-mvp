# Database Migrations

## How to Apply Migrations

Migrations need to be run manually in the Supabase SQL Editor.

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Run the migrations in order:

### Initial Setup
```sql
-- Run migrations/init.sql first (if not already done)
```

### Two-Tab Architecture (2025-01-XX)
```sql
-- Run migrations/add_list_type.sql
-- This adds the list_type column and migrates existing data
```

## Migration History

- `init.sql` - Initial database schema with grocery_items table
- `add_list_type.sql` - Add two-tab architecture (To Buy / Items lists)

## Important Notes

- Always backup your database before running migrations
- Migrations are designed to preserve existing data
- The `add_list_type.sql` migration will:
  - Add `list_type` column with default 'to_buy'
  - Migrate bought items to 'items' list
  - Migrate unbought items to 'to_buy' list
  - Keep the `is_bought` field for backward compatibility
