"""
Social Media Skills for Gold Tier Autonomous AI Employee.

Provides social media skills for Twitter, Instagram, and Facebook.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional, List
from src.base_skill import BaseSkill
from mcp_server.twitter_handler import TwitterHandler
from mcp_server.instagram_handler import InstagramHandler
from mcp_server.facebook_handler import FacebookHandler
from src.retry_logic import with_retry
from shared.logging_config import get_logger

logger = get_logger(__name__, "social-skills.log")


class FetchTwitterMetricsSkill(BaseSkill):
    """
    Skill for fetching Twitter engagement metrics.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize Twitter metrics skill."""
        super().__init__(
            name="fetch_twitter_metrics",
            description="Fetch engagement metrics from Twitter",
            risk_level="low"
        )
        self.twitter = TwitterHandler()

    @with_retry(max_attempts=3)
    async def execute(self, days: int = 7, **kwargs) -> Dict[str, Any]:
        """
        Execute Twitter metrics fetch.

        Args:
            days: Number of days to fetch (default: 7)

        Returns:
            Result dictionary with Twitter metrics
        """
        logger.info(f"Fetching Twitter metrics for last {days} days")

        try:
            result = self.twitter.get_engagement_summary(days=days)

            if result.get("success"):
                logger.info("Twitter metrics fetched successfully")
            else:
                logger.error(f"Twitter metrics fetch failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Twitter metrics fetch error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "TWITTER_METRICS_ERROR",
                "message": str(e)
            }


class FetchInstagramMetricsSkill(BaseSkill):
    """
    Skill for fetching Instagram engagement metrics.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize Instagram metrics skill."""
        super().__init__(
            name="fetch_instagram_metrics",
            description="Fetch engagement metrics from Instagram",
            risk_level="low"
        )
        self.instagram = InstagramHandler()

    @with_retry(max_attempts=3)
    async def execute(self, days: int = 7, **kwargs) -> Dict[str, Any]:
        """
        Execute Instagram metrics fetch.

        Args:
            days: Number of days to fetch (default: 7)

        Returns:
            Result dictionary with Instagram metrics
        """
        logger.info(f"Fetching Instagram metrics for last {days} days")

        try:
            result = self.instagram.get_engagement_summary(days=days)

            if result.get("success"):
                logger.info("Instagram metrics fetched successfully")
            else:
                logger.error(f"Instagram metrics fetch failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Instagram metrics fetch error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "INSTAGRAM_METRICS_ERROR",
                "message": str(e)
            }


class FetchFacebookMetricsSkill(BaseSkill):
    """
    Skill for fetching Facebook engagement metrics.

    Risk Level: Low (read-only operation)
    """

    def __init__(self):
        """Initialize Facebook metrics skill."""
        super().__init__(
            name="fetch_facebook_metrics",
            description="Fetch engagement metrics from Facebook",
            risk_level="low"
        )
        self.facebook = FacebookHandler()

    @with_retry(max_attempts=3)
    async def execute(self, days: int = 7, **kwargs) -> Dict[str, Any]:
        """
        Execute Facebook metrics fetch.

        Args:
            days: Number of days to fetch (default: 7)

        Returns:
            Result dictionary with Facebook metrics
        """
        logger.info(f"Fetching Facebook metrics for last {days} days")

        try:
            result = self.facebook.get_engagement_summary(days=days)

            if result.get("success"):
                logger.info("Facebook metrics fetched successfully")
            else:
                logger.error(f"Facebook metrics fetch failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Facebook metrics fetch error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "FACEBOOK_METRICS_ERROR",
                "message": str(e)
            }


class GenerateWeeklySocialSummarySkill(BaseSkill):
    """
    Skill for generating weekly social media summary.

    Risk Level: Low (read-only aggregation)
    """

    def __init__(self):
        """Initialize weekly social summary skill."""
        super().__init__(
            name="generate_weekly_social_summary",
            description="Generate weekly social media performance summary",
            risk_level="low"
        )
        self.twitter = TwitterHandler()
        self.instagram = InstagramHandler()
        self.facebook = FacebookHandler()

    @with_retry(max_attempts=3)
    async def execute(self, days: int = 7, **kwargs) -> Dict[str, Any]:
        """
        Execute weekly social summary generation.

        Args:
            days: Number of days to summarize (default: 7)

        Returns:
            Result dictionary with aggregated social metrics
        """
        logger.info(f"Generating weekly social summary for last {days} days")

        try:
            # Fetch metrics from all platforms
            twitter_result = self.twitter.get_engagement_summary(days=days)
            instagram_result = self.instagram.get_engagement_summary(days=days)
            facebook_result = self.facebook.get_engagement_summary(days=days)

            # Aggregate results
            summary = {
                "success": True,
                "period_days": days,
                "platforms": {
                    "twitter": twitter_result if twitter_result.get("success") else {"success": False, "error": "unavailable"},
                    "instagram": instagram_result if instagram_result.get("success") else {"success": False, "error": "unavailable"},
                    "facebook": facebook_result if facebook_result.get("success") else {"success": False, "error": "unavailable"}
                },
                "total_engagement": 0,
                "total_reach": 0,
                "top_platform": None
            }

            # Calculate totals
            for platform, data in summary["platforms"].items():
                if data.get("success"):
                    platform_summary = data.get("summary", {})
                    summary["total_engagement"] += platform_summary.get("total_engagements", 0)
                    summary["total_reach"] += platform_summary.get("total_reach", 0)

            # Determine top platform
            platform_engagements = {}
            for platform, data in summary["platforms"].items():
                if data.get("success"):
                    platform_engagements[platform] = data.get("summary", {}).get("total_engagements", 0)

            if platform_engagements:
                summary["top_platform"] = max(platform_engagements, key=platform_engagements.get)

            logger.info(f"Weekly social summary generated: {summary['total_engagement']} total engagements")
            return summary

        except Exception as e:
            logger.error(f"Weekly social summary generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "SOCIAL_SUMMARY_ERROR",
                "message": str(e)
            }


class PostToTwitterSkill(BaseSkill):
    """
    Skill for posting to Twitter.

    Risk Level: High (public visibility)
    """

    def __init__(self):
        """Initialize Twitter posting skill."""
        super().__init__(
            name="post_to_twitter",
            description="Post a message to Twitter",
            risk_level="high"
        )
        self.twitter = TwitterHandler()

    @with_retry(max_attempts=2)
    async def execute(self, message: str, media_urls: Optional[List[str]] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute Twitter post.

        Args:
            message: Tweet text (max 280 characters)
            media_urls: Optional media URLs

        Returns:
            Result dictionary with post status
        """
        logger.info(f"Posting to Twitter: {message[:50]}...")

        try:
            # Validate message length
            if len(message) > 280:
                return {
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "Tweet exceeds 280 character limit"
                }

            result = self.twitter.post_twitter(
                message=message,
                media_urls=media_urls
            )

            if result.get("success"):
                logger.info("Twitter post successful")
            else:
                logger.error(f"Twitter post failed: {result.get('message')}")

            return result

        except Exception as e:
            logger.error(f"Twitter post error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "TWITTER_POST_ERROR",
                "message": str(e)
            }


# Export all social media skills
__all__ = [
    "FetchTwitterMetricsSkill",
    "FetchInstagramMetricsSkill",
    "FetchFacebookMetricsSkill",
    "GenerateWeeklySocialSummarySkill",
    "PostToTwitterSkill"
]
