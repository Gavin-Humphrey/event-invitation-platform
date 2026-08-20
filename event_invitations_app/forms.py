from django import forms
from django.forms import inlineformset_factory
from .models import RSVP, AdditionalGuest, Event

GUEST_CHOICES = (
    (1, '1 Guest (Just Me)'),
    (2, '2 Guests'),
    (3, '3 Guests (Max Limit)'),
)


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
            'full_name',
            'email',
            'phone',
            'attending',
            'guest_count',
            'dietary_requirements',
            'message',
        ]
        widgets = {
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
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guest Full Name'}),
        }


AdditionalGuestFormSet = inlineformset_factory(
    RSVP,
    AdditionalGuest,
    form=AdditionalGuestForm,
    extra=2,
    max_num=2,
    can_delete=False
)