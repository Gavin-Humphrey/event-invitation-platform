import re
from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator
from .models import GalleryImage, RSVP, AdditionalGuest, Event



class RSVPUpdateForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = '__all__'

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image', 'caption', 'category']

GUEST_CHOICES = (
    (1, '1 Guest (Just Me)'),
    (2, '2 Guests'),
    (3, '3 Guests (Max Limit)'),
)

# Regex Validators
name_validator = RegexValidator(
    regex=r"^[a-zA-Z\s'-]+$",
    message="Name can only contain letters, spaces, hyphens, and apostrophes."
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
    message="Enter a valid phone number (e.g., +1234567890 or 08012345678)."
)

# Standard email regex pattern matching RFC 5322 specs
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class RSVPForm(forms.ModelForm):
    passcode = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter invitation passcode',
            'style': 'text-transform: uppercase;'
        }),
        label="INVITATION PASSCODE *"
    )

    guest_count = forms.TypedChoiceField(
        choices=GUEST_CHOICES,
        coerce=int,
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_guest_count'}),
        label="NUMBER OF GUESTS ATTENDING (MAX 3) *"
    )

    class Meta:
        model = RSVP
        fields = [
            'passcode',
            'suffix',
            'full_name',
            'email',
            'phone',
            'attending',
            'guest_count',
            'dietary_requirements',
            'message',
        ]
        widgets = {
            'suffix': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'attending': forms.RadioSelect(attrs={'class': 'radio-input'}),
            'dietary_requirements': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'List any dietary restrictions or allergies'
            }),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your birthday message here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attach field validators dynamically
        self.fields['full_name'].validators.append(name_validator)
        self.fields['phone'].validators.append(phone_validator)

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name) < 2:
            raise forms.ValidationError("Please enter a valid full name (at least 2 characters).")
        return full_name.title()  # Formats name cleanly (e.g., "john doe" -> "John Doe")

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if email and not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Uniqueness Check
        if email:
            query = RSVP.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)

            if query.exists():
                raise forms.ValidationError("An RSVP with this email address has already been submitted.")

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        if phone and not phone.startswith('+'):
            raise forms.ValidationError("Please include your country prefix starting with '+' (e.g., +33 6 12 34 56 78).")

        cleaned_phone = re.sub(r"[\s\-\(\)]", "", phone)

        if len(cleaned_phone) < 8:
            raise forms.ValidationError("Phone number is too short.")

        # Uniqueness Check
        if cleaned_phone:
            query = RSVP.objects.filter(phone=cleaned_phone)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)

            if query.exists():
                raise forms.ValidationError("An RSVP with this phone number has already been submitted.")

        return cleaned_phone

    def clean_passcode(self):
        code_input = self.cleaned_data.get('passcode', '').strip().upper()
        
        # Fetch valid passcode set in Django Admin (Event model)
        event = Event.objects.first()
        valid_code = event.invitation_passcode.strip().upper() if (event and event.invitation_passcode) else "JERRY80"

        if code_input != valid_code:
            raise forms.ValidationError("Invalid invitation passcode. Please check your invitation card.")
        
        return code_input


class AdditionalGuestForm(forms.ModelForm):
    class Meta:
        model = AdditionalGuest
        fields = ['full_name']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Guest Full Name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attach the regex validator dynamically
        self.fields['full_name'].validators.append(name_validator)

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        
        # If the form is optional in a formset, pass through empty entries
        if not full_name:
            return full_name

        if len(full_name) < 2:
            raise forms.ValidationError("Additional guest name must be at least 2 characters long.")

        return full_name.title() 

AdditionalGuestFormSet = inlineformset_factory(
    RSVP,
    AdditionalGuest,
    form=AdditionalGuestForm,
    extra=2,
    max_num=2,
    can_delete=False
)