# Deploy History Rename to Production

## Current Status
- ✅ Database is ready (list_type column added, data migrated, indexes created)
- ✅ Code is ready on branch `claude/clarify-two-tab-architecture-012hcSwkVEmBhfmX7d3rPz8P`
- ❌ Production still shows "Items" tab

## Deploy Steps

### Option A: Via Pull Request (Recommended)
1. Create PR from `claude/clarify-two-tab-architecture-012hcSwkVEmBhfmX7d3rPz8P` to `main`
2. Review changes
3. Merge PR
4. Railway will auto-deploy to production

### Option B: Direct Merge
```bash
# Switch to main
git checkout main

# Pull latest
git pull origin main

# Merge the feature branch
git merge claude/clarify-two-tab-architecture-012hcSwkVEmBhfmX7d3rPz8P

# Push to trigger deployment
git push origin main
```

## Post-Deployment Verification

1. Visit https://grocery-list-mvp-production.up.railway.app
2. Login
3. Verify you see two tabs:
   - "To Buy" (shopping list)
   - "History" (purchase history)
4. Test functionality:
   - Add item in To Buy tab
   - Move item to History using arrow button
   - Move item back to To Buy
   - Verify tab counts update correctly

## Rollback Plan (if needed)

If anything breaks:
```bash
git checkout main
git revert HEAD
git push origin main
```

This will revert back to showing "Items" tab while we debug.
