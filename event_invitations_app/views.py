from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from .models import Event, RSVP, GalleryImage
from .forms import RSVPForm, AdditionalGuestFormSet, RSVPUpdateForm, GalleryImageForm
from django.db.models import Sum

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




def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser, login_url='/admin/login/')
def admin_dashboard(request):
    event = Event.objects.first()
    rsvps = RSVP.objects.all().order_by('-id')
    gallery_images = GalleryImage.objects.all().order_by('-id')

    if request.method == 'POST' and 'upload_image' in request.POST:
        image_form = GalleryImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            gallery_item = image_form.save(commit=False)
            gallery_item.event = event
            gallery_item.save()
            messages.success(request, "Gallery image uploaded successfully.")
            return redirect('admin_dashboard')
    else:
        image_form = GalleryImageForm()


    # Sum total guest_count for all attending RSVPs
    total_attending_headcount = RSVP.objects.filter(
        attending='YES'
    ).aggregate(
        total=Sum('guest_count')
    )['total'] or 0

    context = {
        'rsvps': rsvps,
        'gallery_images': gallery_images,
        'image_form': image_form,
        'total_attending_headcount': total_attending_headcount,
    }
    return render(request, 'dashboard.html', context)

@user_passes_test(is_superuser, login_url='/admin/login/')
def edit_rsvp(request, pk):
    rsvp = get_object_or_404(RSVP, pk=pk)
    if request.method == 'POST':
        form = RSVPUpdateForm(request.POST, instance=rsvp)
        if form.is_valid():
            form.save()
            messages.success(request, f"RSVP #{rsvp.pk} updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = RSVPUpdateForm(instance=rsvp)

    return render(request, 'edit_rsvp.html', {'form': form, 'rsvp': rsvp})


@user_passes_test(is_superuser, login_url='/admin/login/')
def view_rsvp(request, pk):
    rsvp = get_object_or_404(RSVP, pk=pk)
    # Retrieves all additional guests linked to this RSVP (if using a ForeignKey or formset relation)
    additional_guests = rsvp.additional_guests.all() if hasattr(rsvp, 'additional_guests') else []

    context = {
        'rsvp': rsvp,
        'additional_guests': additional_guests,
    }
    return render(request, 'view_rsvp.html', context)

@user_passes_test(is_superuser, login_url='/admin/login/')
def delete_gallery_image(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        image.image.delete()  # Removes physical media file
        image.delete()        # Removes database record
        messages.success(request, "Image deleted successfully.")
    return redirect('admin_dashboard')


# def rsvp_confirmation_mail():
