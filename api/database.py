import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Global anon client (current approach - will be replaced)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase() -> Client:
    """
    Dependency to get Supabase client.
    Currently returns anon client.
    Will be replaced with authenticated client.
    """
    return supabase


def get_authenticated_supabase(access_token: str) -> Client:
    """
    Create a Supabase client authenticated with user's access token.
    This allows RLS policies to work correctly.
    
    Args:
        access_token: User's JWT access token from Supabase auth
        
    Returns:
        Authenticated Supabase client with auth.uid() context
    """
    print(f"\n[AUTH CLIENT] Creating authenticated Supabase client")
    print(f"[AUTH CLIENT] Token length: {len(access_token)}")
    
    # Create new client with user's token
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Set the session with user's token - this sets auth.uid() context
    client.auth.set_session(access_token, access_token)  # Both access and refresh
    
    print(f"[AUTH CLIENT] ✅ Authenticated client created")
    print(f"[AUTH CLIENT] Client type: {type(client)}")
    
    return client