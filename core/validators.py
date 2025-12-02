"""
Custom validators for ReefGuard application.

Provides validators for file uploads and other data validation.
"""
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import os


@deconstructible
class FileValidator:
    """
    Validator for file uploads with size and type restrictions.
    """
    # 10 MB max file size
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Allowed file extensions for images
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    # Allowed file extensions for videos
    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']

    def __init__(self, max_size=MAX_FILE_SIZE, allowed_extensions=None):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or (
            self.IMAGE_EXTENSIONS + self.VIDEO_EXTENSIONS
        )

    def __call__(self, value):
        """
        Validate the uploaded file.

        Args:
            value: The uploaded file object

        Raises:
            ValidationError: If file is invalid
        """
        # Check file size
        if value.size > self.max_size:
            size_mb = self.max_size / (1024 * 1024)
            raise ValidationError(
                f'File size must not exceed {size_mb}MB. '
                f'Your file is {value.size / (1024 * 1024):.2f}MB.'
            )

        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f'File type "{ext}" is not allowed. '
                f'Allowed types: {", ".join(self.allowed_extensions)}'
            )

        return value


@deconstructible
class ImageValidator(FileValidator):
    """
    Validator specifically for image files.
    """
    def __init__(self, max_size=5 * 1024 * 1024):  # 5MB for images
        super().__init__(
            max_size=max_size,
            allowed_extensions=self.IMAGE_EXTENSIONS
        )


@deconstructible
class VideoValidator(FileValidator):
    """
    Validator specifically for video files.
    """
    def __init__(self, max_size=50 * 1024 * 1024):  # 50MB for videos
        super().__init__(
            max_size=max_size,
            allowed_extensions=self.VIDEO_EXTENSIONS
        )


def validate_latitude(value):
    """Validate latitude is within valid range."""
    if not -90 <= value <= 90:
        raise ValidationError(
            f'Latitude must be between -90 and 90 degrees. Got {value}.'
        )


def validate_longitude(value):
    """Validate longitude is within valid range."""
    if not -180 <= value <= 180:
        raise ValidationError(
            f'Longitude must be between -180 and 180 degrees. Got {value}.'
        )
