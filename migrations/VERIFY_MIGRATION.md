# Verify Migration Completed Successfully

Run these queries in Supabase SQL Editor to verify the migration worked correctly.

## 1. Check list_type distribution

```sql
SELECT list_type, COUNT(*) as count
FROM grocery_items
GROUP BY list_type
ORDER BY list_type;
```

**Expected:** You should see rows for 'to_buy' and/or 'history' with counts.

---

## 2. Verify data migration based on is_bought status

```sql
-- Should return 0 rows (all bought items should be in history)
SELECT COUNT(*) as incorrect_bought_items
FROM grocery_items
WHERE is_bought = true AND list_type != 'history';
```

**Expected:** `0` (no bought items in the wrong list)

```sql
-- Should return 0 rows (all unbought items should be in to_buy)
SELECT COUNT(*) as incorrect_unbought_items
FROM grocery_items
WHERE is_bought = false AND list_type != 'to_buy';
```

**Expected:** `0` (no unbought items in the wrong list)

---

## 3. Verify indexes were created

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'grocery_items'
  AND (indexname LIKE '%list_type%' OR indexname LIKE '%user_list%')
ORDER BY indexname;
```

**Expected:** You should see:
- `idx_grocery_items_list_type`
- `idx_grocery_items_user_list`

---

## 4. Sample data check

```sql
-- Show sample items from each list
SELECT list_type, name, is_bought, created_at
FROM grocery_items
ORDER BY list_type, created_at DESC
LIMIT 10;
```

**Expected:** Items are correctly distributed between 'to_buy' and 'history'.

---

## All checks passed?

If all verification queries show expected results:
✅ **Migration is complete!**

Your app should now be working with the two-tab architecture:
- **To Buy tab**: Shows unbought items (your shopping list)
- **History tab**: Shows bought items (purchase history)

You can test the app by:
1. Loading the app - both tabs should show correct counts
2. Adding items - they should appear in "To Buy"
3. Moving items between tabs using arrow buttons
4. Checking items off in "To Buy" tab (strikethrough)
