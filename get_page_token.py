"""
Get Facebook Page Access Token
Retrieves the Page Access Token from your user token
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*60)
    print("GET FACEBOOK PAGE ACCESS TOKEN")
    print("="*60)
    print()

    user_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not user_token:
        print("[ERROR] No token found in .env")
        return

    print("Step 1: Getting your pages...")
    try:
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={user_token}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"[ERROR] Failed to get pages: {response.text}")
            return

        data = response.json()
        pages = data.get('data', [])

        if not pages:
            print("[ERROR] No pages found")
            print("\nYour token needs these permissions:")
            print("  - pages_manage_posts")
            print("  - pages_read_engagement")
            print("\nGet a new token from: https://developers.facebook.com/tools/explorer/")
            return

        print(f"[OK] Found {len(pages)} page(s)\n")

        for i, page in enumerate(pages, 1):
            print(f"Page {i}: {page.get('name')}")
            print(f"  Page ID: {page.get('id')}")
            print(f"  Category: {page.get('category', 'N/A')}")
            print(f"\n  Page Access Token:")
            print(f"  {page.get('access_token')}")
            print()
            print("="*60)
            print("UPDATE YOUR .ENV FILE:")
            print("="*60)
            print(f"FACEBOOK_PAGE_ID={page.get('id')}")
            print(f"FACEBOOK_PAGE_ACCESS_TOKEN={page.get('access_token')}")
            print("="*60)
            print()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
