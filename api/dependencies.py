from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from database import get_supabase, get_authenticated_supabase
import traceback

security = HTTPBearer()

# TOGGLE: Set to True to use authenticated client, False for anon client
USE_AUTHENTICATED_CLIENT = False


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> str:
    """
    Extract and verify user from Supabase JWT token.
    Returns the user's UUID.
    
    LOGGING STRATEGY:
    - Step 1: Log token extraction
    - Step 2: Log Supabase client type (anon vs authenticated)
    - Step 3: Log auth verification result
    - Step 4: Log user ID extraction
    """
    token = credentials.credentials
    
    try:
        print(f"\n{'='*60}")
        print(f"[AUTH STEP 1] Token extracted from request")
        print(f"[AUTH STEP 1] Token length: {len(token)}")
        print(f"[AUTH STEP 1] Token prefix: {token[:20]}...")
        print(f"[AUTH STEP 1] Token suffix: ...{token[-20:]}")
        
        print(f"\n[AUTH STEP 2] Using Supabase client")
        print(f"[AUTH STEP 2] USE_AUTHENTICATED_CLIENT: {USE_AUTHENTICATED_CLIENT}")
        print(f"[AUTH STEP 2] Client type: {type(supabase)}")
        print(f"[AUTH STEP 2] Client URL: {supabase.supabase_url}")
        
        print(f"\n[AUTH STEP 3] Verifying token with Supabase")
        # Verify token and get user
        response = supabase.auth.get_user(token)
        
        print(f"[AUTH STEP 3] Response type: {type(response)}")
        print(f"[AUTH STEP 3] Response user: {response.user}")
        
        if not response.user:
            print("[AUTH STEP 3] ❌ No user in response")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        print(f"\n[AUTH STEP 4] ✅ User verified successfully")
        print(f"[AUTH STEP 4] User ID: {response.user.id}")
        print(f"[AUTH STEP 4] User email: {response.user.email}")
        print(f"{'='*60}\n")
        
        return response.user.id
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n[AUTH ERROR] ❌ Authentication failed")
        print(f"[AUTH ERROR] Error type: {type(e)}")
        print(f"[AUTH ERROR] Error message: {str(e)}")
        print(f"[AUTH ERROR] Traceback:\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_user_supabase_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Client:
    """
    Get authenticated Supabase client for the current user.
    This client will have proper auth.uid() context for RLS.
    
    Returns:
        Authenticated Supabase client if USE_AUTHENTICATED_CLIENT is True,
        otherwise returns anon client.
    """
    token = credentials.credentials
    
    print(f"\n[CLIENT FACTORY] Getting Supabase client")
    print(f"[CLIENT FACTORY] USE_AUTHENTICATED_CLIENT: {USE_AUTHENTICATED_CLIENT}")
    
    if USE_AUTHENTICATED_CLIENT:
        print(f"[CLIENT FACTORY] Creating authenticated client with user token")
        client = get_authenticated_supabase(token)
        print(f"[CLIENT FACTORY] ✅ Returning authenticated client")
        return client
    else:
        print(f"[CLIENT FACTORY] Using anon client (old behavior)")
        client = get_supabase()
        print(f"[CLIENT FACTORY] ✅ Returning anon client")
        return client