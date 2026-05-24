import base64
import sys
import json
from pathlib import Path
from windows.supabase_known_faces import SupabaseKnownFacesCache

def main():
    config_path = Path.home() / ".lumiai" / "config.json"
    if not config_path.exists():
        print(f"Error: Config not found at {config_path}")
        return 1
    
    # Use utf-8-sig to handle potential BOM
    content = config_path.read_text(encoding="utf-8-sig")
    config = json.loads(content)

    project_url = config.get("supabase_project_url")
    api_key = config.get("supabase_api_key")

    if not project_url or not api_key:
        print("Error: Missing Supabase configuration.")
        return 1

    cache = SupabaseKnownFacesCache(project_url=project_url, api_key=api_key)
    
    img_path = Path("download.jpg")
    if not img_path.exists():
        print(f"Error: {img_path} not found.")
        return 1

    with open(img_path, "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode("ascii")

    try:
        print(f"Uploading {img_path} to Supabase images table...")
        row = cache.insert_image_base64(image_name="download", image_base64=img_base64)
        print(f"Successfully uploaded. Image ID: {row.get('id')}")
    except Exception as e:
        print(f"Failed to upload: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
