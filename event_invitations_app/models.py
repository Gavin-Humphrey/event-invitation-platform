from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models



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

    def __str__(self):
        return self.title

class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('about', 'About Dad'),
        ('memory', '80 Years'),
    ]

    event = models.ForeignKey(Event, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.caption or f"Gallery Image {self.pk}"


class RSVP(models.Model):
    # Renamed to HONORIFIC_CHOICES or PREFIX_SUFFIX_CHOICES for clarity
    SUFFIX_CHOICES = [
        ('', 'None'),
        ('Chief', 'Chief'),
        ('Rev.', 'Rev.'),
        ('Dr.', 'Dr.'),
        ('Eng.', 'Eng.'),
        ('Esq.', 'Esq.'),
        ('Mr & Mrs', 'Mr & Mrs'),
        ('Jr.', 'Jr.'),
        ('Sr.', 'Sr.'),
    ]

    class AttendingStatus(models.TextChoices):
        YES = 'YES', 'Yes, I will be attending'
        NO = 'NO', 'No, I will not be attending'

    event = models.ForeignKey('Event', related_name='rsvps', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)  # Renamed from full_name to avoid conflict
    suffix = models.CharField(max_length=20, choices=SUFFIX_CHOICES, blank=True, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    attending = models.CharField(
        max_length=3, 
        choices=AttendingStatus.choices, 
        default=AttendingStatus.YES
    )
    guest_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
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

    guest_count = models.PositiveSmallIntegerField(default=1)
    
    @property
    def total_guests(self):
        """Returns total party size (primary guest + additional guests)."""
        if self.attending == 'YES':  
            return self.guest_count
        return 0

    @property
    def display_name(self):
        """Returns name with prefix/suffix applied correctly."""
        if not self.suffix:
            return self.full_name
        
        if self.suffix in ['Chief', 'Rev.', 'Dr.', 'Eng.', 'Mr & Mrs']:
            return f"{self.suffix} {self.full_name}"
        return f"{self.full_name} {self.suffix}"

    def __str__(self):
        return self.display_name


class AdditionalGuest(models.Model):
    rsvp = models.ForeignKey(RSVP, related_name='additional_guests', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return f"Guest: {self.full_name} (RSVP: {self.rsvp.full_name})"