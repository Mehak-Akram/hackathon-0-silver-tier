"""
Social Media Monitor
Monitors social media platforms for mentions and creates tasks
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger


class SocialMediaMonitor:
    """
    Monitors social media platforms for mentions and engagement opportunities
    """

    def __init__(self):
        """Initialize social media monitor"""
        self.inbox_path = Path('./Inbox')
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        self.audit_logger = AuditLogger()
        self.processed_mentions_file = Path('./Audit_Logs/processed_mentions.json')

        # Load processed mention IDs
        self.processed_mentions = self._load_processed_mentions()

        # Platform configurations
        self.platforms = {
            'facebook': {
                'enabled': os.getenv('FACEBOOK_MONITORING_ENABLED', 'false').lower() == 'true',
                'page_id': os.getenv('FACEBOOK_PAGE_ID'),
                'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN')
            },
            'twitter': {
                'enabled': os.getenv('TWITTER_MONITORING_ENABLED', 'false').lower() == 'true',
                'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
            },
            'instagram': {
                'enabled': os.getenv('INSTAGRAM_MONITORING_ENABLED', 'false').lower() == 'true',
                'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
                'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
            }
        }

    def _load_processed_mentions(self) -> set:
        """Load set of already processed mention IDs"""
        if self.processed_mentions_file.exists():
            try:
                data = json.loads(self.processed_mentions_file.read_text())
                return set(data.get('processed_ids', []))
            except:
                return set()
        return set()

    def _save_processed_mention(self, mention_id: str):
        """Save mention ID as processed"""
        self.processed_mentions.add(mention_id)

        self.processed_mentions_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_mentions_file.write_text(json.dumps({
            'processed_ids': list(self.processed_mentions),
            'last_updated': datetime.now().isoformat()
        }, indent=2))

    def check_facebook_mentions(self) -> List[Dict[str, Any]]:
        """
        Check Facebook page for new mentions and comments

        Returns:
            List of new mentions
        """
        if not self.platforms['facebook']['enabled']:
            return []

        mentions = []

        try:
            # In production, use Facebook Graph API to fetch:
            # - Page mentions
            # - Post comments
            # - Direct messages

            # Simulated mention for development
            mention_id = f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            if mention_id not in self.processed_mentions:
                mention = {
                    'platform': 'facebook',
                    'mention_id': mention_id,
                    'type': 'comment',
                    'from_user': 'John Doe',
                    'from_user_id': 'fb_user_123',
                    'message': 'Great product! Can you tell me more about pricing?',
                    'post_id': 'fb_post_456',
                    'timestamp': datetime.now().isoformat()
                }
                mentions.append(mention)

        except Exception as e:
            self.audit_logger.log_event(
                event_type='facebook_check_error',
                details={'error': str(e)},
                severity='error'
            )

        return mentions

    def check_twitter_mentions(self) -> List[Dict[str, Any]]:
        """
        Check Twitter for new mentions

        Returns:
            List of new mentions
        """
        if not self.platforms['twitter']['enabled']:
            return []

        mentions = []

        try:
            # In production, use Twitter API v2 to fetch:
            # - Mentions timeline
            # - Direct messages

            # Simulated mention for development
            mention_id = f"tw_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            if mention_id not in self.processed_mentions:
                mention = {
                    'platform': 'twitter',
                    'mention_id': mention_id,
                    'type': 'mention',
                    'from_user': '@customer123',
                    'from_user_id': 'tw_user_789',
                    'message': '@YourBrand I have a question about your service',
                    'tweet_id': 'tw_tweet_101',
                    'timestamp': datetime.now().isoformat()
                }
                mentions.append(mention)

        except Exception as e:
            self.audit_logger.log_event(
                event_type='twitter_check_error',
                details={'error': str(e)},
                severity='error'
            )

        return mentions

    def check_instagram_mentions(self) -> List[Dict[str, Any]]:
        """
        Check Instagram for new mentions and comments

        Returns:
            List of new mentions
        """
        if not self.platforms['instagram']['enabled']:
            return []

        mentions = []

        try:
            # In production, use Instagram Graph API to fetch:
            # - Post comments
            # - Story mentions
            # - Direct messages

            # Simulated mention for development
            mention_id = f"ig_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            if mention_id not in self.processed_mentions:
                mention = {
                    'platform': 'instagram',
                    'mention_id': mention_id,
                    'type': 'comment',
                    'from_user': 'customer_jane',
                    'from_user_id': 'ig_user_456',
                    'message': 'Love this! Where can I buy?',
                    'post_id': 'ig_post_789',
                    'timestamp': datetime.now().isoformat()
                }
                mentions.append(mention)

        except Exception as e:
            self.audit_logger.log_event(
                event_type='instagram_check_error',
                details={'error': str(e)},
                severity='error'
            )

        return mentions

    def classify_mention(self, mention: Dict[str, Any]) -> str:
        """
        Classify mention type

        Args:
            mention: Mention data

        Returns:
            Mention classification
        """
        message = mention.get('message', '').lower()

        # Customer inquiry keywords
        inquiry_keywords = [
            'question', 'how', 'what', 'where', 'when', 'why',
            'price', 'pricing', 'cost', 'buy', 'purchase', 'order',
            'help', 'support', 'issue', 'problem'
        ]

        # Sales keywords
        sales_keywords = [
            'interested', 'demo', 'trial', 'quote', 'information'
        ]

        # Check for customer inquiry
        if any(keyword in message for keyword in inquiry_keywords):
            return 'customer_inquiry'

        # Check for sales opportunity
        if any(keyword in message for keyword in sales_keywords):
            return 'sales_opportunity'

        # Positive engagement
        positive_keywords = ['love', 'great', 'awesome', 'amazing', 'excellent']
        if any(keyword in message for keyword in positive_keywords):
            return 'positive_engagement'

        return 'general_mention'

    def create_task_from_mention(self, mention: Dict[str, Any]) -> Path:
        """
        Create task file from social media mention

        Args:
            mention: Mention data

        Returns:
            Path to created task file
        """
        mention_type = self.classify_mention(mention)
        platform = mention.get('platform')

        # Create task
        task = {
            'type': 'social_media_mention',
            'classified_type': 'social_media',
            'platform': platform,
            'content': f"Social media mention from {mention.get('from_user')} on {platform}",
            'mention_id': mention.get('mention_id'),
            'mention_type': mention_type,
            'from_user': mention.get('from_user'),
            'from_user_id': mention.get('from_user_id'),
            'message': mention.get('message'),
            'post_id': mention.get('post_id'),
            'timestamp': datetime.now().isoformat(),
            'requires_response': mention_type in ['customer_inquiry', 'sales_opportunity']
        }

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"social_mention_{platform}_{timestamp}.json"
        task_path = self.inbox_path / filename

        # Write task
        task_path.write_text(json.dumps(task, indent=2))

        self.audit_logger.log_event(
            event_type='social_media_task_created',
            details={
                'file': filename,
                'platform': platform,
                'from_user': mention.get('from_user'),
                'mention_type': mention_type
            },
            severity='info'
        )

        return task_path

    def check_all_platforms(self) -> int:
        """
        Check all enabled social media platforms for new mentions

        Returns:
            Number of tasks created
        """
        all_mentions = []

        # Check each platform
        all_mentions.extend(self.check_facebook_mentions())
        all_mentions.extend(self.check_twitter_mentions())
        all_mentions.extend(self.check_instagram_mentions())

        tasks_created = 0

        for mention in all_mentions:
            try:
                mention_id = mention.get('mention_id')

                # Skip if already processed
                if mention_id in self.processed_mentions:
                    continue

                # Create task
                self.create_task_from_mention(mention)
                tasks_created += 1

                # Mark as processed
                self._save_processed_mention(mention_id)

            except Exception as e:
                self.audit_logger.log_event(
                    event_type='social_media_task_creation_error',
                    details={
                        'platform': mention.get('platform'),
                        'from_user': mention.get('from_user'),
                        'error': str(e)
                    },
                    severity='error'
                )

        if tasks_created > 0:
            print(f"[Social Media Monitor] Created {tasks_created} tasks from mentions")

        return tasks_created


def main():
    """Test social media monitor"""
    print("="*60)
    print("SOCIAL MEDIA MONITOR TEST")
    print("="*60)

    monitor = SocialMediaMonitor()

    print("\nChecking social media platforms...")
    count = monitor.check_all_platforms()

    print(f"\n[OK] Processed {count} new mentions")
    print("\nTasks created in Inbox/ folder")
    print("\n[INFO] Enable platforms in .env:")
    print("  FACEBOOK_MONITORING_ENABLED=true")
    print("  TWITTER_MONITORING_ENABLED=true")
    print("  INSTAGRAM_MONITORING_ENABLED=true")


if __name__ == "__main__":
    main()
