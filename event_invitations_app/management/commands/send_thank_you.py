from django.core.management.base import BaseCommand
from event_invitations_app.models import RSVP
from event_invitations_app.sms import send_sms_batch


class Command(BaseCommand):
    help = "Send a thank you SMS to guests for attending the birthday event."

    def handle(self, *args, **options):
        confirmed_rsvps = RSVP.objects.filter(
            attending=RSVP.AttendingStatus.YES
        ).exclude(
            phone=""
        )

        message_text = (
            "A huge THANK YOU to everyone who came out to celebrate dad’s 80th birthday with us yesterday. "
            "To everyone who travelled, showed up, supported us, helped behind the scenes, and went above and beyond to make the day so special. "
            "The love you showed my dad and our entire family meant more than words can express. "
            "You helped make his 80th birthday an unforgettable celebration filled with love, laughter, joy, and beautiful memories. "
            "May God richly bless each and every one of you for celebrating this incredible milestone with us. "
            "We appreciate you all more than you know. "
            "Thank you from the bottom of our hearts!"
        )
        
        messages = [
            {
                "recipient": rsvp.phone,
                "content": message_text,
            }
            for rsvp in confirmed_rsvps
        ]

        if not messages:
            self.stdout.write(
                self.style.WARNING(
                    "No confirmed RSVPs with phone numbers found."
                )
            )
            return

        success = send_sms_batch(messages)

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Thank you SMS successfully sent to {len(messages)} recipient(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Failed to send the thank you SMS batch."
                )
            )