"""
Social Media Post model for Gold Tier Autonomous AI Employee.

Represents content on social platforms.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SocialPlatform(str, Enum):
    """Social media platforms."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"


class PostStatus(str, Enum):
    """Post status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class PostType(str, Enum):
    """Post content type."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"
    STORY = "story"


class SocialMediaPost(BaseModel):
    """
    Social Media Post entity representing content on social platforms.

    Attributes:
        post_id: Unique post identifier
        external_id: Platform-specific post ID
        platform: Social media platform
        post_type: Type of post content
        status: Post status

        content: Post text content
        media_urls: List of media URLs (images/videos)
        link_url: Shared link URL
        hashtags: List of hashtags

        post_date: Date post was published
        scheduled_date: Date post is scheduled for

        engagement_metrics: Engagement data (likes, shares, comments, etc.)
        performance_score: Calculated performance score (0-100)

        author_id: Author identifier
        author_name: Author name

        metadata: Additional post metadata
    """

    post_id: str = Field(..., description="Unique post identifier")
    external_id: Optional[str] = Field(default=None, description="Platform post ID")
    platform: SocialPlatform = Field(..., description="Social platform")
    post_type: PostType = Field(default=PostType.TEXT, description="Post type")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")

    # Content
    content: str = Field(..., description="Post text content")
    media_urls: List[str] = Field(default_factory=list, description="Media URLs")
    link_url: Optional[str] = Field(default=None, description="Shared link")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags")

    # Dates
    post_date: Optional[datetime] = Field(default=None, description="Published date")
    scheduled_date: Optional[datetime] = Field(default=None, description="Scheduled date")

    # Engagement
    engagement_metrics: Dict[str, int] = Field(
        default_factory=lambda: {
            "likes": 0,
            "shares": 0,
            "comments": 0,
            "reach": 0,
            "impressions": 0,
            "clicks": 0,
            "saves": 0
        },
        description="Engagement metrics"
    )
    performance_score: float = Field(default=0.0, description="Performance score (0-100)")

    # Author
    author_id: Optional[str] = Field(default=None, description="Author ID")
    author_name: Optional[str] = Field(default=None, description="Author name")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True

    def mark_published(self, external_id: str, post_date: Optional[datetime] = None) -> None:
        """
        Mark post as published.

        Args:
            external_id: Platform-specific post ID
            post_date: Publication date
        """
        self.status = PostStatus.PUBLISHED
        self.external_id = external_id
        self.post_date = post_date or datetime.now()

    def mark_failed(self, error: str) -> None:
        """
        Mark post as failed.

        Args:
            error: Error message
        """
        self.status = PostStatus.FAILED
        self.metadata["error"] = error

    def mark_scheduled(self, scheduled_date: datetime) -> None:
        """
        Mark post as scheduled.

        Args:
            scheduled_date: Scheduled publication date
        """
        self.status = PostStatus.SCHEDULED
        self.scheduled_date = scheduled_date

    def update_engagement(self, metrics: Dict[str, int]) -> None:
        """
        Update engagement metrics.

        Args:
            metrics: Engagement metrics dictionary
        """
        self.engagement_metrics.update(metrics)
        self.performance_score = self.calculate_performance_score()

    def calculate_performance_score(self) -> float:
        """
        Calculate performance score based on engagement.

        Returns:
            Performance score (0-100)
        """
        metrics = self.engagement_metrics

        # Weighted scoring
        likes_score = min(metrics.get("likes", 0) / 100, 1.0) * 20
        shares_score = min(metrics.get("shares", 0) / 50, 1.0) * 25
        comments_score = min(metrics.get("comments", 0) / 30, 1.0) * 25
        reach_score = min(metrics.get("reach", 0) / 1000, 1.0) * 15
        clicks_score = min(metrics.get("clicks", 0) / 100, 1.0) * 15

        total_score = likes_score + shares_score + comments_score + reach_score + clicks_score
        return round(total_score, 2)

    def get_engagement_rate(self) -> float:
        """
        Calculate engagement rate.

        Returns:
            Engagement rate (0-1)
        """
        reach = self.engagement_metrics.get("reach", 0)
        if reach == 0:
            return 0.0

        total_engagement = (
            self.engagement_metrics.get("likes", 0) +
            self.engagement_metrics.get("shares", 0) +
            self.engagement_metrics.get("comments", 0)
        )

        return total_engagement / reach

    def get_total_engagement(self) -> int:
        """
        Get total engagement count.

        Returns:
            Total engagement
        """
        return (
            self.engagement_metrics.get("likes", 0) +
            self.engagement_metrics.get("shares", 0) +
            self.engagement_metrics.get("comments", 0)
        )

    def is_high_performing(self, threshold: float = 70.0) -> bool:
        """
        Check if post is high-performing.

        Args:
            threshold: Performance score threshold

        Returns:
            True if post exceeds threshold
        """
        return self.performance_score >= threshold

    def extract_hashtags(self) -> List[str]:
        """
        Extract hashtags from content.

        Returns:
            List of hashtags
        """
        import re
        hashtags = re.findall(r'#(\w+)', self.content)
        return hashtags

    def add_hashtag(self, hashtag: str) -> None:
        """
        Add hashtag to post.

        Args:
            hashtag: Hashtag to add (without #)
        """
        if hashtag not in self.hashtags:
            self.hashtags.append(hashtag)

    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert post to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialMediaPost":
        """
        Create post from dictionary.

        Args:
            data: Post data dictionary

        Returns:
            SocialMediaPost instance
        """
        return cls(**data)

    @classmethod
    def from_twitter_data(cls, twitter_data: Dict[str, Any]) -> "SocialMediaPost":
        """
        Create post from Twitter API data.

        Args:
            twitter_data: Twitter API response data

        Returns:
            SocialMediaPost instance
        """
        metrics = twitter_data.get("public_metrics", {})

        return cls(
            post_id=f"twitter_{twitter_data.get('id')}",
            external_id=twitter_data.get("id"),
            platform=SocialPlatform.TWITTER,
            post_type=PostType.TEXT,
            status=PostStatus.PUBLISHED,
            content=twitter_data.get("text", ""),
            post_date=datetime.fromisoformat(twitter_data.get("created_at", "").replace("Z", "+00:00")),
            engagement_metrics={
                "likes": metrics.get("like_count", 0),
                "shares": metrics.get("retweet_count", 0),
                "comments": metrics.get("reply_count", 0),
                "impressions": metrics.get("impression_count", 0)
            }
        )

    @classmethod
    def from_instagram_data(cls, instagram_data: Dict[str, Any]) -> "SocialMediaPost":
        """
        Create post from Instagram API data.

        Args:
            instagram_data: Instagram API response data

        Returns:
            SocialMediaPost instance
        """
        return cls(
            post_id=f"instagram_{instagram_data.get('id')}",
            external_id=instagram_data.get("id"),
            platform=SocialPlatform.INSTAGRAM,
            post_type=PostType.IMAGE,
            status=PostStatus.PUBLISHED,
            content=instagram_data.get("caption", ""),
            media_urls=[instagram_data.get("media_url", "")],
            post_date=datetime.fromisoformat(instagram_data.get("timestamp", "").replace("Z", "+00:00")),
            engagement_metrics={
                "likes": instagram_data.get("like_count", 0),
                "comments": instagram_data.get("comments_count", 0),
                "reach": instagram_data.get("reach", 0)
            }
        )
