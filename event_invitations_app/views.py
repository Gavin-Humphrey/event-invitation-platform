from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from .models import Event, RSVP, GalleryImage
from .forms import RSVPForm, AdditionalGuestFormSet, RSVPUpdateForm, GalleryImageForm
from django.db.models import Sum

from django.conf import settings
from django.core.mail import send_mail

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, date
from django.views.decorators.csrf import ensure_csrf_cookie



@ensure_csrf_cookie
def home(request):

    event, _ = Event.objects.get_or_create(
        pk=1,
        defaults={
            "title": "Chief Jerry's 80th Birthday Celebration",
            "event_date": datetime(2026, 10, 3, 17, 0),
            "venue_name": "PRINCE REGENT HOTEL, Manor Rd, Chigwell, Essex IG8 8AE",
            "rsvp_deadline": date(2026, 9, 20),
            "invitation_passcode": "JERRY80",
        }
    )

    # Fetch uploaded gallery images for the event
    gallery_images = GalleryImage.objects.filter(event=event).order_by('-id')

    # Fetch ALL messages (attending and declined)
    confirmed_messages = RSVP.objects.filter(
        event=event
    ).exclude(
        message__exact=''
    ).exclude(
        message__isnull=True
    ).order_by('-created_at')

    if request.method == 'POST':
        form = RSVPForm(request.POST)
        dummy_rsvp = RSVP(event=event)
        formset = AdditionalGuestFormSet(request.POST, instance=dummy_rsvp)

        if form.is_valid() and formset.is_valid():
            rsvp = form.save(commit=False)
            rsvp.event = event

            # Check attendance status
            is_attending = rsvp.attending in ["YES", getattr(RSVP.AttendingStatus, "YES", "YES")]

            # Zero out headcount if declining
            if not is_attending:
                rsvp.guest_count = 0

            rsvp.save()

            recipient_name = rsvp.full_name if rsvp.full_name else "Valued Guest"
            greeting_prefix = f"{rsvp.suffix} " if rsvp.suffix else ""

            if is_attending:
                guest_count = form.cleaned_data.get('guest_count', 1)
                dietary_requirements = form.cleaned_data.get('dietary_requirements', 'None')
                additional_guests = formset.save(commit=False)

                for i, guest in enumerate(additional_guests):
                    if i < (guest_count - 1):
                        guest.rsvp = rsvp
                        guest.save()

                subject = "RSVP Confirmed - We look forward to seeing you!"

                html_content = f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #C5A059; border-radius: 8px; overflow: hidden;">
                    <div style="background-color: #0B2B1D; padding: 24px; text-align: center;">
                        <h1 style="color: #C5A059; margin: 0; font-size: 22px; letter-spacing: 1px; text-transform: uppercase;">
                            RSVP Confirmed
                        </h1>
                    </div>
                    <div style="padding: 30px; background-color: #ffffff; color: #333333; line-height: 1.6;">
                        <p style="font-size: 16px; margin-top: 0;">
                            Dear <strong>{greeting_prefix}{recipient_name}</strong>,
                        </p>
                        <p>
                            Thank you for confirming your attendance! We are thrilled and delighted that you will be joining us to celebrate.
                        </p>
                        <div style="background-color: #F9F6F0; border-left: 4px solid #C5A059; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; font-weight: bold; color: #0B2B1D;">Summary of your reservation:</p>
                            <p style="margin: 5px 0 0 0;">Total Guests: <strong>{guest_count}</strong></p>
                            <p style="margin: 5px 0 0 0;">Dietary Requirements: <strong>{dietary_requirements}</strong></p>
                            <p style="margin: 5px 0 0 0;">Date: <strong>3rd of October 2026</strong></p>
                            <p style="margin: 5px 0 0 0;">Event Venue: <strong>PRINCE REGENT HOTEL<br>Manor Rd, Chigwell, Essex IG8 8AE</strong></p>
                            <p style="margin: 5px 0 0 0;">Event Time: <strong>5 pm (UK).</strong>  * No African time.</p>
                        </div>
                        <p>We look forward to welcoming you!</p>
                        <p style="margin-top: 30px;">
                            Warm regards,<br>
                            <strong>Event Hosting Committee</strong>
                        </p>
                    </div>
                </div>
                """

                plain_message = (
                    f"Dear {greeting_prefix}{recipient_name},\n\n"
                    f"Thank you for confirming your attendance! We are thrilled and delighted that you will be joining us to celebrate.\n\n"
                    f"Summary of your reservation:\n"
                    f"- Total Guests: {guest_count}\n"
                    f"- Dietary Requirements: {dietary_requirements}\n\n"
                    f"We look forward to welcoming you!\n\n"
                    f"Warm regards,\n"
                    f"Event Hosting Committee"
                )

            else:
                subject = "Thank you for your response"

                html_content = f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px;">
                    <p style="font-size: 16px; margin-top: 0;">
                        Dear <strong>{greeting_prefix}{recipient_name}</strong>,
                    </p>
                    <p>
                        Thank you for letting us know. We are sorry you won't be able to make it, but we appreciate your response!
                    </p>
                    <p style="margin-top: 30px;">
                        Warm regards,<br>
                        <strong>Event Hosting Committee</strong>
                    </p>
                </div>
                """

                plain_message = (
                    f"Dear {greeting_prefix}{recipient_name},\n\n"
                    f"Thank you for letting us know. We are sorry you won't be able to make it, but we appreciate your response!\n\n"
                    f"Warm regards,\n"
                    f"Event Hosting Committee"
                )

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[rsvp.email],
                html_message=html_content,
                fail_silently=False,
            )

            messages.success(
                request,
                "Thank you for your RSVP! Your response has been successfully received.",
            )
            return redirect("home")

    else:
        form = RSVPForm()
        formset = AdditionalGuestFormSet(instance=RSVP())

    return render(
        request, 
        "index.html", 
        {
            "event": event, 
            "form": form, 
            "formset": formset, 
            "gallery_images": gallery_images,
            "confirmed_messages": confirmed_messages
        }
    )
#########


# def is_superuser(user):
#     return user.is_authenticated and user.is_superuser

def is_admin_user(user):
    return user.is_authenticated and user.is_active and (user.is_superuser or user.is_staff)


@user_passes_test(is_admin_user, login_url='admin:login')
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

# @user_passes_test(is_superuser, login_url='/admin/login/')

@user_passes_test(is_admin_user, login_url='admin:login')
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


#@user_passes_test(is_superuser, login_url='/admin/login/')
@user_passes_test(is_admin_user, login_url='admin:login')
def view_rsvp(request, pk):
    rsvp = get_object_or_404(RSVP, pk=pk)
    # Retrieves all additional guests linked to this RSVP (if using a ForeignKey or formset relation)
    additional_guests = rsvp.additional_guests.all() if hasattr(rsvp, 'additional_guests') else []

    context = {
        'rsvp': rsvp,
        'additional_guests': additional_guests,
    }
    return render(request, 'view_rsvp.html', context)

@user_passes_test(is_admin_user, login_url='admin:login')
def delete_gallery_image(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    
    # Safely attempt to delete physical/cloud file
    try:
        image.image.delete(save=False)
    except Exception as e:
        # Ignore errors if the old local file doesn't exist on Cloudinary
        print(f"Skipping storage delete for old media item: {e}")

    # Remove the database record
    image.delete()
    
    # Redirect back to your dashboard (use your actual URL pattern name)
    return redirect('admin_dashboard')  # or 'event_invitations_app:dashboard'

@user_passes_test(is_admin_user, login_url='admin:login')
def edit_gallery_image(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)

    if request.method == 'POST':
        # Pass request.FILES for optional new image uploads, and instance=image for existing data
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        
        if form.is_valid():
            # If a new image file was uploaded, clean up the old file from storage first
            if 'image' in form.changed_data and request.FILES.get('image'):
                try:
                    # Get the old file instance from database prior to saving new one
                    old_image = GalleryImage.objects.get(pk=pk)
                    old_image.image.delete(save=False)
                except Exception as e:
                    print(f"Skipping storage delete for old file: {e}")

            form.save()
            return redirect('admin_dashboard')
    else:
        # Pre-populate the form with existing model instance
        form = GalleryImageForm(instance=image)

    context = {
        'form': form,
        'gallery_image': image,
    }
    return render(request, 'edit_gallery_image.html', context)