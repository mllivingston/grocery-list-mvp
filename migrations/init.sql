-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grocery Items Table
CREATE TABLE grocery_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    is_bought BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster user queries
CREATE INDEX idx_grocery_items_user_id ON grocery_items(user_id);
CREATE INDEX idx_grocery_items_created_at ON grocery_items(created_at DESC);

-- Row Level Security (RLS)
ALTER TABLE grocery_items ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own items
CREATE POLICY "Users can view own items"
    ON grocery_items FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own items
CREATE POLICY "Users can insert own items"
    ON grocery_items FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own items
CREATE POLICY "Users can update own items"
    ON grocery_items FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own items
CREATE POLICY "Users can delete own items"
    ON grocery_items FOR DELETE
    USING (auth.uid() = user_id);
