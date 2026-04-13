"""
Test Facebook Post
Quick script to test Facebook posting functionality
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_server.facebook_handler import FacebookHandler


def main():
    print("="*60)
    print("FACEBOOK POST TEST")
    print("="*60)
    print()

    try:
        # Initialize handler
        print("Initializing Facebook handler...")
        handler = FacebookHandler()
        print("[OK] Handler initialized")
        print(f"  Page ID: {handler.page_id}")
        print(f"  API Version: {handler.api_version}")
        print()

        # Create test message (emojis will display on Facebook, not console)
        test_message = f"""🤖 Gold Tier Autonomous Employee - Test Post

This is an automated test post from the Gold Tier AI Employee system.

✅ System Status: Operational
📅 Posted: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
🎯 Purpose: Testing Facebook integration

#AI #Automation #GoldTier"""

        print("Posting to Facebook...")
        print(f"Message length: {len(test_message)} characters")
        print()

        # Post to Facebook
        result = handler.post_facebook_page(
            message=test_message,
            published=True
        )

        # Display result
        if result.get('success'):
            print("="*60)
            print("[SUCCESS] Post published!")
            print("="*60)
            print(f"Post ID: {result.get('post_id')}")
            print(f"Post URL: {result.get('post_url')}")
            print(f"Timestamp: {result.get('timestamp')}")
            print()
            print("Visit your Facebook page to see the post!")
        else:
            print("="*60)
            print("[FAILED] Post not published")
            print("="*60)
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            print(f"Timestamp: {result.get('timestamp')}")

    except Exception as e:
        print("="*60)
        print("[ERROR]")
        print("="*60)
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
