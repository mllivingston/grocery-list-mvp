# Complete the Existing Migration

The `list_type` column already exists from a previous migration attempt.
Run these remaining steps **ONE AT A TIME** in Supabase SQL Editor.

## Step 1: Migrate bought items to 'history' list

```sql
UPDATE grocery_items SET list_type = 'history' WHERE is_bought = true;
```

**Expected result:** Success message showing how many rows updated

---

## Step 2: Migrate unbought items to 'to_buy' list

```sql
UPDATE grocery_items SET list_type = 'to_buy' WHERE is_bought = false;
```

**Expected result:** Success message showing how many rows updated

---

## Step 3: Add index on list_type (if not exists)

```sql
CREATE INDEX IF NOT EXISTS idx_grocery_items_list_type ON grocery_items(list_type);
```

**Expected result:** Success message (or notice that index already exists)

---

## Step 4: Add composite index (if not exists)

```sql
CREATE INDEX IF NOT EXISTS idx_grocery_items_user_list ON grocery_items(user_id, list_type);
```

**Expected result:** Success message (or notice that index already exists)

---

## Verification

After running all steps, verify the migration worked:

```sql
SELECT list_type, COUNT(*) as count FROM grocery_items GROUP BY list_type;
```

**Expected result:** You should see counts for 'to_buy' and 'history' lists

---

## What This Does

- Moves all previously-bought items to the "History" tab
- Keeps all unbought items in the "To Buy" tab
- Adds performance indexes for faster queries
- The app will immediately start working with the two-tab architecture
