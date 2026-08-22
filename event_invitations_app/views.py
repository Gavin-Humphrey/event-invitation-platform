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
            dietary_requirements = form.cleaned_data.get('dietary_requirements')
            # event_date = form.cleaned_data.get('event_date')
            # venue_name = form.cleaned_data.get('venue_name')
            additional_guests = formset.save(commit=False)

            for i, guest in enumerate(additional_guests):
                if i < (guest_count - 1):
                    guest.rsvp = rsvp
                    guest.save()

            recipient_name = rsvp.full_name if rsvp.full_name else "Valued Guest"
            greeting_prefix = f"{rsvp.suffix} " if rsvp.suffix else ""

            if rsvp.attending == "YES":
                # 1. Cleaner subject line (removing initial emoji prevents spam filter triggers on new domains)
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
                            <p style="margin: 5px 0 0 0;">Event Venue: <strong>PRINCE REGENT HOTEL
                                Manor Rd, Chigwell, Essex IG8 8AE</strong></p>
                            <p style="margin: 5px 0 0 0;">Event Time: <strong>5 pm</strong>  * No African time.</p>
                        </div>
                        <p>We look forward to welcoming you!</p>
                        <p style="margin-top: 30px;">
                            Warm regards,<br>
                            <strong>Event Hosting Committee</strong>
                        </p>
                    </div>
                </div>
                """

                # 2. Complete plain text version matching the HTML structure (crucial for inbox delivery)
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

            # Send via Resend / Anymail
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[rsvp.email],
                html_message=html_content,
                fail_silently=False,
            )

            # Add success message for the modal pop-up
            messages.success(
                request,
                "Thank you for your RSVP! Your response has been successfully received.",
            )
            return redirect("home")  # Redirect to prevent form resubmission

    else:
        form = RSVPForm()
        formset = AdditionalGuestFormSet(instance=RSVP())

    return render(
        request, "index.html", {"event": event, "form": form, "formset": formset}
    )


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
