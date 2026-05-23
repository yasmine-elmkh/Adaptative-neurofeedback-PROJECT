import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qwxkhkumyokzykykindv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eGtoa3VteW9renlreWtpbmR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY4NTYyMiwiZXhwIjoyMDk0MjYxNjIyfQ.t0TAfEJfgeMqmBXh2UwOT4kU0ukZKf7I7IvlwMKHNHQ")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)