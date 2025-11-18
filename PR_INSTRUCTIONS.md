# Create New PR to Apply History Rename

## Current Situation

The branch `claude/clarify-two-tab-architecture-012hcSwkVEmBhfmX7d3rPz8P` has all the History rename changes, but main doesn't.

When PR #12 was merged, it only brought in the migration guide files, not the actual code changes to rename "Items" → "History". This happened because of the revert that occurred earlier.

## Solution: Create New Pull Request

### Step 1: Create PR on GitHub

1. Go to https://github.com/mllivingston/grocery-list-mvp/pulls
2. Click **"New pull request"**
3. Set:
   - **Base**: `main`
   - **Compare**: `claude/clarify-two-tab-architecture-012hcSwkVEmBhfmX7d3rPz8P`
4. Title: **"Apply History rename to codebase (database migration complete)"**

### Step 2: PR Description

```markdown
## Summary
This PR applies the "Items" → "History" rename throughout the codebase. The database migration has been completed and verified.

## What Will Change
- ✅ Frontend: Tab label changes from "Items" to "History"
- ✅ Backend: API endpoints updated (`items` → `history`)
- ✅ All JavaScript references updated
- ✅ Documentation updated (CHANGELOG, migration files)

## Database Status
- ✅ `list_type` column exists
- ✅ Data migrated successfully (21 to_buy, 7 history)
- ✅ Indexes created
- ✅ Data integrity verified

## Why New PR?
PR #12 brought in the migration guides but didn't include the code changes due to the previous revert. This PR completes the rename.

## Test Plan
After merge:
- [ ] Deploy and verify "History" tab appears in production
- [ ] Test moving items between To Buy and History tabs
- [ ] Verify tab counts are accurate
```

### Step 3: Review Changes

The PR will show changes in these files:
- `api/static/index.html` - Frontend tab name and JavaScript
- `api/models.py` - API model types
- `api/main.py` - Endpoint validation and comments
- `CHANGELOG.md` - Documentation updates
- `migrations/add_list_type.sql` - Migration comments
- `migrations/README.md` - Migration documentation

### Step 4: Merge and Deploy

Once merged, Railway will automatically deploy and production will show "History" instead of "Items".

## Files Changed Summary

```
api/static/index.html        | 18 +++++++++---------
api/main.py                  | 10 +++++-----
api/models.py                |  4 ++--
CHANGELOG.md                 | 18 +++++++++---------
migrations/README.md         |  4 ++--
migrations/add_list_type.sql |  6 +++---
6 files changed, 30 insertions(+), 30 deletions(-)
```

All changes are straightforward find-and-replace of "items"/"Items" with "history"/"History".
