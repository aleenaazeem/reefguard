"""
Models for ReefGuard application.

Contains models for:
- CustomUser (with roles: Admin, Researcher, Student)
- Reef (coral reef locations and info)
- Event (monitoring events, pollution reports, etc.)
- Article (educational content)
- ImageGallery (photos and videos)
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    """
    Custom user model with role-based access.
    Extends Django's AbstractUser to add role field.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('researcher', 'Researcher'),
        ('student', 'Student'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text='User role for permission levels'
    )
    bio = models.TextField(blank=True, help_text='User biography')
    organization = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Reef(models.Model):
    """
    Coral reef location and monitoring information.
    """
    REGION_CHOICES = [
        ('caribbean', 'Caribbean'),
        ('pacific', 'Pacific'),
        ('indian', 'Indian Ocean'),
        ('red_sea', 'Red Sea'),
        ('atlantic', 'Atlantic'),
    ]

    name = models.CharField(max_length=200, help_text='Reef name')
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    description = models.TextField(help_text='Detailed reef description')
    area_km2 = models.FloatField(
        help_text='Reef area in square kilometers',
        validators=[MinValueValidator(0)]
    )
    depth_meters = models.FloatField(
        help_text='Average depth in meters',
        validators=[MinValueValidator(0)]
    )
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        default='fair'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reefs_created'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reef'
        verbose_name_plural = 'Reefs'

    def __str__(self):
        return f"{self.name} ({self.region})"


class Event(models.Model):
    """
    Monitoring events including pollution reports, coral sightings, etc.
    """
    EVENT_TYPE_CHOICES = [
        ('pollution', 'Pollution Report'),
        ('sighting', 'Coral Sighting'),
        ('bleaching', 'Coral Bleaching'),
        ('restoration', 'Restoration Activity'),
        ('monitoring', 'Monitoring Survey'),
        ('damage', 'Physical Damage'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    reef = models.ForeignKey(
        Reef,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    event_date = models.DateField(help_text='Date when event occurred')
    reported_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events_reported'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text='Additional notes')

    class Meta:
        ordering = ['-event_date', '-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} - {self.reef.name} ({self.event_date})"


class Article(models.Model):
    """
    Educational articles about coral reefs and conservation.
    """
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('research', 'Research'),
        ('news', 'News'),
        ('conservation', 'Conservation'),
        ('restoration', 'Restoration'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = models.TextField()
    excerpt = models.TextField(
        max_length=300,
        help_text='Short summary for article listing'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title


class ImageGallery(models.Model):
    """
    Image and video gallery for reef documentation.
    """
    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]

    reef = models.ForeignKey(
        Reef,
        on_delete=models.CASCADE,
        related_name='gallery_items',
        null=True,
        blank=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='gallery_items',
        null=True,
        blank=True
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='uploads/%Y/%m/',
        help_text='Upload photo or video file'
    )
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploads'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Gallery Item'
        verbose_name_plural = 'Gallery Items'

    def __str__(self):
        return f"{self.title} ({self.media_type})"


class ReefBookmark(models.Model):
    """
    User bookmarks/favorites for reefs.
    Allows users to save reefs for quick access.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reef_bookmarks'
    )
    reef = models.ForeignKey(
        Reef,
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        help_text='Personal notes about this reef'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'reef']
        verbose_name = 'Reef Bookmark'
        verbose_name_plural = 'Reef Bookmarks'

    def __str__(self):
        return f"{self.user.username} - {self.reef.name}"
