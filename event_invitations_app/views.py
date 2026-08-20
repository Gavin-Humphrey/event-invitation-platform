from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Event, RSVP
from .forms import RSVPForm, AdditionalGuestFormSet


def home(request):
    event, _ = Event.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = RSVPForm(request.POST)
        dummy_rsvp = RSVP(event=event)
        formset = AdditionalGuestFormSet(request.POST, instance=dummy_rsvp)

        if form.is_valid() and formset.is_valid():
            rsvp = form.save(commit=False)
            rsvp.event = event
            rsvp.save()

            guest_count = form.cleaned_data.get('guest_count', 1)
            additional_guests = formset.save(commit=False)

            for i, guest in enumerate(additional_guests):
                if i < (guest_count - 1):
                    guest.rsvp = rsvp
                    guest.save()

            # Add success message for the modal pop-up
            messages.success(
                request, 
                "Thank you for your RSVP! Your response has been successfully received."
            )
            return redirect('home')  # Redirect to prevent form resubmission

    else:
        form = RSVPForm()
        formset = AdditionalGuestFormSet(instance=RSVP())

    return render(request, 'index.html', {'event': event, 'form': form, 'formset': formset})