"""
Forms for ReefGuard application.

Includes forms for:
- User registration
- Pollution reports
- Coral sightings
- Contact form
- Image/video uploads
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Event, ImageGallery
from .validators import FileValidator


class UserRegistrationForm(UserCreationForm):
    """
    Custom user registration form with role selection.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    organization = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'organization', 'bio', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class PollutionReportForm(forms.ModelForm):
    """
    Form for reporting pollution events.
    """
    class Meta:
        model = Event
        fields = [
            'reef', 'title', 'description', 'severity',
            'event_date', 'notes'
        ]
        widgets = {
            'reef': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for the pollution event'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the pollution observed'
            }),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or observations'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set event_type to pollution automatically
        self.instance.event_type = 'pollution'


class CoralSightingForm(forms.ModelForm):
    """
    Form for reporting coral sightings.
    """
    class Meta:
        model = Event
        fields = [
            'reef', 'title', 'description', 'event_date', 'notes'
        ]
        widgets = {
            'reef': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What did you observe?'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the coral species, health, and location details'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional observations'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set event_type to sighting and severity to low by default
        self.instance.event_type = 'sighting'
        self.instance.severity = 'low'


class ContactForm(forms.Form):
    """
    General contact form for inquiries.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Your message'
        })
    )


class ImageUploadForm(forms.ModelForm):
    """
    Form for uploading images and videos to the gallery with validation.
    """
    file = forms.FileField(
        validators=[FileValidator()],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
        }),
        help_text='Max file size: 10MB for images, 50MB for videos. Allowed: JPG, PNG, GIF, MP4, MOV'
    )

    class Meta:
        model = ImageGallery
        fields = ['reef', 'event', 'media_type', 'title', 'description', 'file']
        widgets = {
            'reef': forms.Select(attrs={
                'class': 'form-control',
            }),
            'event': forms.Select(attrs={
                'class': 'form-control',
            }),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title for this media'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe what this shows'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make reef and event optional
        self.fields['reef'].required = False
        self.fields['event'].required = False

        # Add help text to fields
        self.fields['reef'].help_text = 'Optional: Associate this media with a specific reef'
        self.fields['event'].help_text = 'Optional: Link this media to an event'
        self.fields['media_type'].help_text = 'Select whether this is a photo or video'

    def clean(self):
        """Additional validation for file uploads."""
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        file = cleaned_data.get('file')

        if file and media_type:
            file_ext = file.name.split('.')[-1].lower()

            if media_type == 'photo' and file_ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
                raise forms.ValidationError(
                    'You selected "Photo" but uploaded a video file. Please select "Video" as media type.'
                )
            elif media_type == 'video' and file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                raise forms.ValidationError(
                    'You selected "Video" but uploaded an image file. Please select "Photo" as media type.'
                )

        return cleaned_data
