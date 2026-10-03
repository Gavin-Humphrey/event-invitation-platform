from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from cloudinary.utils import cloudinary_url
from django.utils import timezone
from zoneinfo import ZoneInfo



class Event(models.Model):
    title = models.CharField(max_length=200, default="Chief Jerry's 80th Birthday Celebration")
    event_date = models.DateTimeField()
    venue_name = models.CharField(max_length=200)
    rsvp_deadline = models.DateField()
    
    # Passcode managed directly via admin
    invitation_passcode = models.CharField(
        max_length=50, 
        default="JERRY80", 
        help_text="Shared passcode required for guests to submit an RSVP"
    )

    live_access_code = models.CharField(
        max_length=50,
        default="JERRYLIVE",
        help_text="Code required to access the live event and livestream"
    )

    live_stream_link = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        help_text="Optional link for virtual attendance (Zoom, YouTube, Google Meet, etc.)"
    )

    def __str__(self):
        return self.title

    # @property
    # def is_live_day(self):
    #     """Returns True only if today matches the calendar date of the event."""
    #     if not self.event_date:
    #         return False
    #     event_local_date = timezone.localtime(self.event_date).date()
    #     today_local_date = timezone.localdate()
    #     return event_local_date == today_local_date

    @property
    def is_live_day(self):
        """Returns True only if today matches the event date in UK time."""

        if not self.event_date:
            return False

        uk_timezone = ZoneInfo("Europe/London")

        event_uk_date = timezone.localtime(
            self.event_date,
            uk_timezone
        ).date()

        today_uk_date = timezone.localdate(uk_timezone)

        return event_uk_date == today_uk_date

    @property
    def is_past(self):
        """Returns True if the event date has already passed."""
        if not self.event_date:
            return False
        return timezone.localtime(self.event_date).date() < timezone.localdate()


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('about', 'About Dad'),
        ('memory', '80 Years'),
    ]

    event = models.ForeignKey(Event, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='birthday_gallery/')
    description = models.CharField(max_length=200, blank=True, null=True, help_text="Image description (max 200 chars)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='about')

    def __str__(self):
        return self.description or f"Gallery Image {self.pk}"


class RSVP(models.Model):
    SUFFIX_CHOICES = [
        ('', 'None'),
        ('Mr.', 'Mr.'),
        ('Mr & Mrs', 'Mr & Mrs'),
        ('Mrs.', 'Mrs.'),
        ('Miss', 'Miss'),
        ('Nze', 'Nze'),
        ('Chief', 'Chief'),
        ('Rev.', 'Rev.'),
        ('Dr.', 'Dr.'),
        ('Eng.', 'Eng.'),
        ('Esq.', 'Esq.'),
        ('Jr.', 'Jr.'),
        ('Sr.', 'Sr.'),
    ]

    class AttendingStatus(models.TextChoices):
        YES = 'YES', 'Yes, I will be attending'
        NO = 'NO', 'No, I will not be attending'

    event = models.ForeignKey('Event', related_name='rsvps', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    suffix = models.CharField(max_length=20, choices=SUFFIX_CHOICES, blank=True, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    attending = models.CharField(
        max_length=3, 
        choices=AttendingStatus.choices, 
        default=AttendingStatus.YES
    )
    # Set MinValueValidator(0) so zero headcount for declined RSVPs is valid
    guest_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )
    dietary_requirements = models.TextField(
        blank=True, 
        help_text="Dietary restrictions or allergies for primary guest or party"
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    @property
    def total_guests(self):
        """Returns total party size (primary guest + additional guests)."""
        if self.attending == self.AttendingStatus.YES:  
            return self.guest_count
        return 0

    @property
    def display_name(self):
        """Returns name with prefix/suffix applied correctly."""
        if not self.suffix:
            return self.full_name
        
        # Prefixes (appear before name)
        if self.suffix in ['Mr.', 'Mrs.', 'Miss', 'Chief', 'Rev.', 'Dr.', 'Eng.', 'Mr & Mrs']:
            return f"{self.suffix} {self.full_name}"
        # Suffixes (appear after name, e.g., John Doe Jr.)
        return f"{self.full_name} {self.suffix}"

    def __str__(self):
        return self.display_name


class AdditionalGuest(models.Model):
    rsvp = models.ForeignKey(RSVP, related_name='additional_guests', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return f"Guest: {self.full_name} (RSVP: {self.rsvp.full_name})"