from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from supabase import Client
from uuid import UUID
from typing import List, Dict
import os

from database import get_supabase
from dependencies import get_current_user
from models import ItemCreateRequest, ItemResponse, ErrorResponse

app = FastAPI(
    title="Grocery List MVP",
    description="Zero-friction grocery list management",
    version="1.0.0"
)

# CORS middleware for frontend running on different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Keep for backwards compatibility
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check(
    supabase: Client = Depends(get_supabase)
) -> Dict:
    """
    Health check endpoint - verify auth and Supabase connection.
    No authentication required.
    """
    print(f"\n{'='*60}")
    print(f"[HEALTH CHECK] Starting health check")
    
    health_status = {
        "status": "healthy",
        "supabase_connected": False,
        "supabase_url": None,
        "supabase_client_type": str(type(supabase)),
        "environment_vars": {
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY"))
        }
    }
    
    try:
        health_status["supabase_url"] = supabase.supabase_url
        health_status["supabase_connected"] = True
        print(f"[HEALTH CHECK] ✅ Supabase client initialized")
        print(f"[HEALTH CHECK] URL: {supabase.supabase_url}")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        print(f"[HEALTH CHECK] ❌ Supabase connection failed: {str(e)}")
    
    print(f"[HEALTH CHECK] Complete: {health_status}")
    print(f"{'='*60}\n")
    
    return health_status


@app.get("/api/items", response_model=List[ItemResponse])
async def get_items(
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all grocery items for the authenticated user.
    Returns both bought and unbought items.
    """
    try:
        print(f"\n[GET ITEMS] Starting for user_id: {user_id}")
        
        response = supabase.table("grocery_items") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at") \
            .execute()
        
        print(f"[GET ITEMS] ✅ Retrieved {len(response.data)} items")
        return response.data
    
    except Exception as e:
        print(f"[GET ITEMS] ❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch items: {str(e)}"
        )


@app.post("/api/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreateRequest,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new grocery item.
    Item is created with is_bought=false by default.
    """
    try:
        print(f"\n[CREATE ITEM] Starting")
        print(f"[CREATE ITEM] Item name: {item.name}")
        print(f"[CREATE ITEM] User ID: {user_id}")
        
        item_data = {
            "user_id": user_id,
            "name": item.name,
            "is_bought": False
        }
        print(f"[CREATE ITEM] Data to insert: {item_data}")
        
        response = supabase.table("grocery_items") \
            .insert(item_data) \
            .execute()
        
        print(f"[CREATE ITEM] Response data: {response.data}")
        
        if not response.data:
            print("[CREATE ITEM] ❌ No data returned from insert")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create item"
            )
        
        print(f"[CREATE ITEM] ✅ Item created: {response.data[0]}")
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CREATE ITEM] ❌ Error: {str(e)}")
        import traceback
        print(f"[CREATE ITEM] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}"
        )

@app.patch("/api/items/{item_id}/toggle", response_model=ItemResponse)
async def toggle_item(
    item_id: UUID,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Toggle the is_bought status of a grocery item.
    Flips between bought/unbought state.
    """
    try:
        print(f"\n[TOGGLE ITEM] Starting for item_id: {item_id}")
        
        # First, get the current item to check ownership and get current state
        item_response = supabase.table("grocery_items") \
            .select("*") \
            .eq("item_id", str(item_id)) \
            .eq("user_id", user_id) \
            .execute()
        
        if not item_response.data:
            print(f"[TOGGLE ITEM] ❌ Item not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        current_item = item_response.data[0]
        new_bought_status = not current_item["is_bought"]
        print(f"[TOGGLE ITEM] Current status: {current_item['is_bought']} → New status: {new_bought_status}")
        
        # Update the item
        update_response = supabase.table("grocery_items") \
            .update({"is_bought": new_bought_status}) \
            .eq("item_id", str(item_id)) \
            .eq("user_id", user_id) \
            .execute()
        
        if not update_response.data:
            print(f"[TOGGLE ITEM] ❌ Update failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle item"
            )
        
        print(f"[TOGGLE ITEM] ✅ Item toggled successfully")
        return update_response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[TOGGLE ITEM] ❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle item: {str(e)}"
        )


@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Permanently delete a grocery item.
    This is optional for cleanup - users can keep items indefinitely.
    """
    try:
        print(f"\n[DELETE ITEM] Starting for item_id: {item_id}")
        
        response = supabase.table("grocery_items") \
            .delete() \
            .eq("item_id", str(item_id)) \
            .eq("user_id", user_id) \
            .execute()
        
        # Supabase returns data even on delete, but if nothing matched, data is empty
        if not response.data:
            print(f"[DELETE ITEM] ❌ Item not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        print(f"[DELETE ITEM] ✅ Item deleted successfully")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DELETE ITEM] ❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}"
        )