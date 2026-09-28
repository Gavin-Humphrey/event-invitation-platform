from datetime import date

from django.core.management.base import BaseCommand

from event_invitations_app.models import RSVP
from event_invitations_app.sms import send_sms_batch


class Command(BaseCommand):
    help = "Send the final birthday SMS reminder to confirmed RSVPs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show recipients without sending SMS.",
        )

    def handle(self, *args, **options):

        if date.today() != date(2026, 10, 2):
            self.stdout.write(
                self.style.WARNING(
                    "Reminder 2 is only allowed to be sent on October 2, 2026."
                )
            )
            return

        confirmed_rsvps = RSVP.objects.filter(
            attending=RSVP.AttendingStatus.YES
        ).exclude(
            phone=""
        )

        reminder = (
            "Good evening 😊 Chief Jerry's 80th birthday celebration is TOMORROW! 🎉 "
            "🕔 5:00 PM — please come early, no African time o! 😄 "
            "📍 Prince Regent Hotel, Manor Road, Woodford, Chigwell, IG8 8AE "
            "See you tomorrow! 🎉"
        )

        messages = [
            {
                "recipient": rsvp.phone,
                "content": reminder,
            }
            for rsvp in confirmed_rsvps
        ]

        if not messages:
            self.stdout.write(
                self.style.WARNING(
                    "No confirmed RSVPs with phone numbers."
                )
            )
            return

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN — {len(messages)} recipient(s) would receive Reminder 2:"
                )
            )

            for message in messages:
                self.stdout.write(
                    f"  {message['recipient']}"
                )

            return

        success = send_sms_batch(messages)

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reminder 2 sent to {len(messages)} recipient(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Reminder 2 failed to send."
                )
            )