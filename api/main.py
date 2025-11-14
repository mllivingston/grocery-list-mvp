from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from supabase import Client
from uuid import UUID
from typing import List, Dict
import os

from database import get_supabase, SUPABASE_URL, SUPABASE_ANON_KEY
from dependencies import get_current_user
from models import ItemCreateRequest, ItemMoveRequest, ItemResponse, ErrorResponse

app = FastAPI(
    title="Grocery List MVP",
    description="Zero-friction grocery list management",
    version="1.0.0"
)

# Serve static files
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    return FileResponse("static/index.html")

# CORS middleware
# In production (Railway), restrict to the specific domain
# In development, allow all origins
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    # Production: restrict to Railway domain
    allowed_origins = [
        f"https://{railway_domain}",
        f"http://{railway_domain}",  # In case HTTP is used
    ]
    print(f"[CORS] Production mode - Allowing origins: {allowed_origins}")
else:
    # Development: allow all origins
    allowed_origins = ["*"]
    print("[CORS] Development mode - Allowing all origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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


@app.get("/api/config")
async def get_config() -> Dict:
    """
    Get frontend configuration (Supabase URL and anon key).
    No authentication required - these are public values.
    """
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY
    }


@app.get("/api/items", response_model=List[ItemResponse])
async def get_items(
    list_type: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Get grocery items for the authenticated user filtered by list type.

    - list_type='to_buy': Returns shopping list (sorted by is_bought ASC, created_at DESC)
    - list_type='items': Returns pantry inventory (sorted alphabetically by name)
    """
    try:
        print(f"\n[GET ITEMS] Starting for user_id: {user_id}, list_type: {list_type}")

        # Validate list_type
        if list_type not in ["to_buy", "items"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="list_type must be 'to_buy' or 'items'"
            )

        # Build query with list_type filter
        query = supabase.table("grocery_items") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("list_type", list_type)

        # Apply sorting based on list type
        if list_type == "to_buy":
            # To Buy: unbought items first (newest first), then bought items (newest first)
            response = query.order("is_bought", desc=False) \
                           .order("created_at", desc=True) \
                           .execute()
        else:
            # Items: alphabetical order
            response = query.order("name", desc=False) \
                           .execute()

        print(f"[GET ITEMS] ✅ Retrieved {len(response.data)} items from {list_type} list")
        return response.data

    except HTTPException:
        raise
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
    Create a new grocery item in the specified list.

    Performs case-insensitive duplicate check before insertion.
    Returns 409 Conflict if item with same name already exists in the target list.
    """
    try:
        print(f"\n[CREATE ITEM] Starting")
        print(f"[CREATE ITEM] Item name: {item.name}")
        print(f"[CREATE ITEM] List type: {item.list_type}")
        print(f"[CREATE ITEM] User ID: {user_id}")

        # Check for case-insensitive duplicates in the target list
        # Using ilike for case-insensitive comparison
        duplicate_check = supabase.table("grocery_items") \
            .select("item_id, name") \
            .eq("user_id", user_id) \
            .eq("list_type", item.list_type) \
            .ilike("name", item.name) \
            .execute()

        if duplicate_check.data:
            print(f"[CREATE ITEM] ❌ Duplicate found: {duplicate_check.data[0]['name']}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'"{item.name}" already exists in this list'
            )

        item_data = {
            "user_id": user_id,
            "name": item.name,
            "list_type": item.list_type,
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
    Only meaningful for items in 'to_buy' list.
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


@app.patch("/api/items/{item_id}/move", response_model=ItemResponse)
async def move_item(
    item_id: UUID,
    move_request: ItemMoveRequest,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Move an item from one list to another (to_buy ↔ items).

    Logic:
    1. Check if item with same name already exists in target list (case-insensitive)
    2. If exists, return 409 Conflict error
    3. If not, create new row in target list with fresh timestamp
    4. Delete original row from source list
    5. Reset is_bought to false on new row
    """
    try:
        print(f"\n[MOVE ITEM] Starting for item_id: {item_id}")
        print(f"[MOVE ITEM] Target list: {move_request.to_list}")

        # Get the current item
        item_response = supabase.table("grocery_items") \
            .select("*") \
            .eq("item_id", str(item_id)) \
            .eq("user_id", user_id) \
            .execute()

        if not item_response.data:
            print(f"[MOVE ITEM] ❌ Item not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        current_item = item_response.data[0]
        item_name = current_item["name"]
        source_list = current_item["list_type"]
        target_list = move_request.to_list

        print(f"[MOVE ITEM] Moving '{item_name}' from '{source_list}' to '{target_list}'")

        # Check if item already exists in target list (case-insensitive)
        duplicate_check = supabase.table("grocery_items") \
            .select("item_id, name") \
            .eq("user_id", user_id) \
            .eq("list_type", target_list) \
            .ilike("name", item_name) \
            .execute()

        if duplicate_check.data:
            print(f"[MOVE ITEM] ❌ Duplicate found in target list")
            list_names = {
                'items': 'inventory',
                'to_buy': 'shopping list'
            }
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'"{item_name}" is already in your {list_names[target_list]}'
            )

        # Create new row in target list with fresh timestamp
        new_item_data = {
            "user_id": user_id,
            "name": item_name,
            "list_type": target_list,
            "is_bought": False  # Reset bought status
        }

        insert_response = supabase.table("grocery_items") \
            .insert(new_item_data) \
            .execute()

        if not insert_response.data:
            print(f"[MOVE ITEM] ❌ Failed to insert into target list")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to move item"
            )

        new_item = insert_response.data[0]
        print(f"[MOVE ITEM] ✅ Created new item in {target_list} with id: {new_item['item_id']}")

        # Delete original item from source list
        delete_response = supabase.table("grocery_items") \
            .delete() \
            .eq("item_id", str(item_id)) \
            .eq("user_id", user_id) \
            .execute()

        if not delete_response.data:
            print(f"[MOVE ITEM] ⚠️ Warning: Failed to delete original item")
            # Note: We don't fail the request here because the new item was created
            # User can manually delete the duplicate if needed

        print(f"[MOVE ITEM] ✅ Move complete: '{item_name}' moved to {target_list}")
        return new_item

    except HTTPException:
        raise
    except Exception as e:
        print(f"[MOVE ITEM] ❌ Error: {str(e)}")
        import traceback
        print(f"[MOVE ITEM] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to move item: {str(e)}"
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