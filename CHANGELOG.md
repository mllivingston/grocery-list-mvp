# Changelog

## [Unreleased] - Two-Tab Architecture

### Added
- **Two-Tab Architecture**: Split single list into "To Buy" (shopping list) and "Items" (pantry inventory)
- **Tab Navigation**: Visual tab switcher with item counts
- **Move Items Between Lists**: Arrow button to transfer items between tabs
- **Case-Insensitive Duplicate Detection**: Prevents adding "Milk", "milk", and "MILK" as separate items
- **List-Specific Sorting**:
  - To Buy: Unbought items first (newest first), then bought items (newest first)
  - Items: Alphabetical order
- **New API Endpoint**: `PATCH /api/items/{id}/move` for moving items between lists
- **Updated API Endpoints**:
  - `GET /api/items` now requires `list_type` query parameter
  - `POST /api/items` now requires `list_type` in request body

### Changed
- **Database Schema**: Added `list_type` column to `grocery_items` table
- **Item Rendering**: Checkbox only appears in "To Buy" tab
- **Placeholder Text**: Changes based on active tab
- **Error Messages**: Specific messages with item names (e.g., "Milk is already in your shopping list")

### Migration Required
Run `migrations/add_list_type.sql` in Supabase SQL Editor to update database schema.

## User Flows

### Flow A: Receipt Scanning (Future)
1. Scan receipt → items extracted
2. Items automatically added to "Items" tab
3. Duplicates silently skipped

### Flow B: Planning Shopping
1. View "Items" tab
2. Click arrow button on "milk" → moves to "To Buy" tab
3. Item stays in "Items" tab, copy created in "To Buy"

### Flow C: During Shopping
1. Open "To Buy" tab
2. Click checkbox on items → strikethrough appears
3. Continue shopping

### Flow D: After Shopping
1. Click arrow button on purchased items → moves back to "Items"
2. Items removed from "To Buy" tab
3. Items appear in "Items" tab (alphabetically sorted)

### Flow E: Manual Add
1. In "To Buy" tab: type "bread" → added to shopping list
2. In "Items" tab: type "flour" → added to inventory
3. Duplicate alerts shown if item already exists

## Technical Details

### Backend Changes
- `api/models.py`: Added `list_type` field and `ItemMoveRequest` model
- `api/main.py`: Updated all endpoints to support two-tab architecture
- `migrations/add_list_type.sql`: Database migration script

### Frontend Changes
- `api/static/index.html`:
  - Added tab navigation UI
  - Implemented tab switching logic
  - Updated item rendering based on active tab
  - Added move button functionality
  - Enhanced error handling for duplicates

### API Breaking Changes
⚠️ **Important**: Clients must update to use the new API:
- `GET /api/items` now requires `?list_type=to_buy` or `?list_type=items`
- `POST /api/items` now requires `{"name": "...", "list_type": "..."}` in body
