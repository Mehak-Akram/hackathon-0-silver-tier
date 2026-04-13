"""
Facebook Configuration Diagnostic
Checks token validity and retrieves correct Page ID
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*60)
    print("FACEBOOK CONFIGURATION DIAGNOSTIC")
    print("="*60)
    print()

    page_id = os.getenv("FACEBOOK_PAGE_ID")
    access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    print(f"Current Page ID: {page_id}")
    print(f"Token configured: {'Yes' if access_token else 'No'}")
    print(f"Token length: {len(access_token) if access_token else 0} characters")
    print()

    if not access_token:
        print("[ERROR] No access token configured")
        return

    # Test 1: Check token validity
    print("Test 1: Checking token validity...")
    try:
        url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Token is valid")
            print(f"  Token belongs to: {data.get('name', 'Unknown')}")
            print(f"  ID: {data.get('id', 'Unknown')}")
        else:
            print(f"[FAILED] Token validation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print()

    # Test 2: Get accounts (pages) this token can access
    print("Test 2: Getting accessible pages...")
    try:
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])

            if pages:
                print(f"[OK] Found {len(pages)} accessible page(s):")
                for i, page in enumerate(pages, 1):
                    print(f"\n  Page {i}:")
                    print(f"    Name: {page.get('name')}")
                    print(f"    ID: {page.get('id')}")
                    print(f"    Category: {page.get('category', 'N/A')}")
                    print(f"    Access Token: {page.get('access_token', 'N/A')[:50]}...")

                    # Check if this matches configured page
                    if page.get('id') == page_id:
                        print(f"    [MATCH] This is your configured page!")
                        print(f"\n[IMPORTANT] Use this Page Access Token in your .env:")
                        print(f"FACEBOOK_PAGE_ACCESS_TOKEN={page.get('access_token')}")
            else:
                print("[WARNING] No pages found. This token might not have page access.")
        else:
            print(f"[FAILED] Could not get pages: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

    print()

    # Test 3: Try to get page info directly
    print("Test 3: Getting page info directly...")
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}?fields=id,name,category&access_token={access_token}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Page found:")
            print(f"  Name: {data.get('name')}")
            print(f"  ID: {data.get('id')}")
            print(f"  Category: {data.get('category')}")
        else:
            print(f"[FAILED] Could not get page info: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

    print()
    print("="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print()
    print("If you see pages listed above:")
    print("1. Copy the Page Access Token from your page")
    print("2. Update FACEBOOK_PAGE_ACCESS_TOKEN in .env")
    print("3. Make sure FACEBOOK_PAGE_ID matches the page ID")
    print()
    print("If no pages are listed:")
    print("1. Your token might be a User Access Token")
    print("2. Get a Page Access Token from Facebook Graph API Explorer")
    print("3. Required permissions: pages_manage_posts, pages_read_engagement")


if __name__ == "__main__":
    main()
