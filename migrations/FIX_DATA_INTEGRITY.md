# Fix Data Integrity Issue

There is 1 item marked as bought but incorrectly placed in the 'to_buy' list.

## Step 1: Identify the problematic item

```sql
SELECT item_id, name, is_bought, list_type, created_at
FROM grocery_items
WHERE is_bought = true AND list_type != 'history';
```

---

## Step 2: Fix it by moving to history

```sql
UPDATE grocery_items
SET list_type = 'history'
WHERE is_bought = true AND list_type != 'history';
```

**Expected result:** `UPDATE 1` (1 row updated)

---

## Step 3: Verify the fix

```sql
-- Should now return 0
SELECT COUNT(*) as incorrect_bought_items
FROM grocery_items
WHERE is_bought = true AND list_type != 'history';
```

**Expected result:** `0`

---

## After fixing

Your data will be fully consistent:
- All bought items → in History tab
- All unbought items → in To Buy tab
- Both performance indexes working
- App fully functional with two-tab architecture
