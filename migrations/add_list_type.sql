-- Add list_type column to grocery_items table
-- Migration for two-tab architecture (To Buy / History)

-- Add list_type column with default 'to_buy'
ALTER TABLE grocery_items
ADD COLUMN list_type TEXT NOT NULL DEFAULT 'to_buy';

-- Migrate existing data based on is_bought status
-- Items that are bought → go to 'history' tab (purchase history)
UPDATE grocery_items
SET list_type = 'history'
WHERE is_bought = true;

-- Items that are not bought → stay in 'to_buy' tab (shopping list)
UPDATE grocery_items
SET list_type = 'to_buy'
WHERE is_bought = false;

-- Add index for faster list_type queries
CREATE INDEX idx_grocery_items_list_type ON grocery_items(list_type);

-- Add composite index for user_id + list_type (most common query pattern)
CREATE INDEX idx_grocery_items_user_list ON grocery_items(user_id, list_type);

-- Note: We keep the is_bought field as it's still meaningful in the 'to_buy' list
-- (for strikethrough during shopping)
