# Diagnose Database State

The `list_type` column already exists. Let's check what state your database is in.

## Step 1: Check if list_type column exists and has data

Run this in Supabase SQL Editor:

```sql
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'grocery_items'
AND column_name = 'list_type';
```

**Expected result:** Should show the column exists with type TEXT

---

## Step 2: Check current list_type values

```sql
SELECT list_type, COUNT(*) as count
FROM grocery_items
GROUP BY list_type;
```

**Possible results:**
- All rows have `'to_buy'` → Migration stopped after adding column
- Mix of `'to_buy'` and `'history'` → Migration partially completed
- Mix of `'to_buy'` and `'items'` → Old migration ran (before rename to "history")
- Empty result → No items in database

---

## Step 3: Check which indexes exist

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'grocery_items'
AND indexname LIKE '%list%';
```

**Expected result:** Should show if list_type indexes were created

---

## Based on Results - Choose Your Path

### Option A: Database has 'items' (old migration)

If Step 2 shows `'items'` instead of `'history'`, you need to rename:

```sql
UPDATE grocery_items SET list_type = 'history' WHERE list_type = 'items';
```

Then verify:
```sql
SELECT list_type, COUNT(*) FROM grocery_items GROUP BY list_type;
```

---

### Option B: Database only has 'to_buy' (incomplete migration)

If Step 2 shows only `'to_buy'`, complete the migration:

```sql
-- Migrate bought items to history
UPDATE grocery_items SET list_type = 'history' WHERE is_bought = true;

-- Verify
SELECT list_type, COUNT(*) FROM grocery_items GROUP BY list_type;
```

---

### Option C: Clean slate (rollback everything)

If you want to start completely fresh:

```sql
-- Drop the column completely
ALTER TABLE grocery_items DROP COLUMN list_type;

-- Verify it's gone
SELECT column_name FROM information_schema.columns
WHERE table_name = 'grocery_items' AND column_name = 'list_type';
```

Then start over with Step 1 from the step-by-step guide.

---

## After Migration is Complete

Add the performance indexes (if they don't already exist):

```sql
-- Check if indexes exist first
SELECT indexname FROM pg_indexes WHERE tablename = 'grocery_items' AND indexname LIKE '%list%';

-- If they don't exist, create them:
CREATE INDEX IF NOT EXISTS idx_grocery_items_list_type ON grocery_items(list_type);
CREATE INDEX IF NOT EXISTS idx_grocery_items_user_list ON grocery_items(user_id, list_type);
```

---

## Verification - Final Check

When everything is complete, run:

```sql
-- Should show two groups: 'to_buy' and 'history'
SELECT list_type, COUNT(*) as count FROM grocery_items GROUP BY list_type;

-- Should show the list_type column
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'grocery_items' ORDER BY ordinal_position;

-- Should show the indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'grocery_items' ORDER BY indexname;
```

Expected results:
- Two list_type values: `'to_buy'` and `'history'`
- Column `list_type` of type `text` exists
- Indexes `idx_grocery_items_list_type` and `idx_grocery_items_user_list` exist
