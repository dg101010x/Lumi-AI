"""Shared Supabase client for GuardianCare modules.

This module provides a single Supabase client instance that all
other modules can import and use for database operations.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and "
        "SUPABASE_KEY in your .env file."
    )

# Single shared client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
