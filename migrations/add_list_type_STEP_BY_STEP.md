# Step-by-Step Migration Guide for list_type Column

Run these SQL statements **ONE AT A TIME** in Supabase SQL Editor.

## Step 1: Add the list_type column

```sql
ALTER TABLE grocery_items ADD COLUMN list_type TEXT NOT NULL DEFAULT 'to_buy';
```

**Expected result:** Success message
**What this does:** Adds the new column with 'to_buy' as default for all existing rows

---

## Step 2: Migrate bought items to 'items' list

```sql
UPDATE grocery_items SET list_type = 'items' WHERE is_bought = true;
```

**Expected result:** Success message showing how many rows updated
**What this does:** Moves all previously-bought items to the "items" list

---

## Step 3: Migrate unbought items to 'to_buy' list

```sql
UPDATE grocery_items SET list_type = 'to_buy' WHERE is_bought = false;
```

**Expected result:** Success message showing how many rows updated
**What this does:** Ensures all unbought items are in "to_buy" list (should already be from default)

---

## Step 4: Add index on list_type

```sql
CREATE INDEX idx_grocery_items_list_type ON grocery_items(list_type);
```

**Expected result:** Success message
**What this does:** Speeds up queries that filter by list_type

---

## Step 5: Add composite index

```sql
CREATE INDEX idx_grocery_items_user_list ON grocery_items(user_id, list_type);
```

**Expected result:** Success message
**What this does:** Speeds up the most common query pattern (user + list_type)

---

## Verification

After running all steps, verify the migration worked:

```sql
SELECT list_type, COUNT(*) as count FROM grocery_items GROUP BY list_type;
```

**Expected result:** You should see counts for 'to_buy' and 'items' lists

---

## Troubleshooting

**If Step 1 fails with "column already exists":**
- The column was partially added before
- Skip to Step 2

**If any UPDATE fails:**
- Check the error message carefully
- Make sure you're in the correct Supabase project

**If indexes fail with "already exists":**
- They were created before
- Skip that step

**To rollback (if needed):**
```sql
-- Remove the column completely
ALTER TABLE grocery_items DROP COLUMN list_type;

-- Remove indexes (if they were created)
DROP INDEX IF EXISTS idx_grocery_items_list_type;
DROP INDEX IF EXISTS idx_grocery_items_user_list;
```
