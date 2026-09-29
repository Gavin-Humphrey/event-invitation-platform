from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Send the scheduled birthday SMS reminder for today's date."

    def handle(self, *args, **options):
        today = date.today()

        self.stdout.write(
            f"Database engine: {connection.settings_dict['ENGINE']}"
        )

        if today == date(2026, 9, 29):
            self.stdout.write(
                "Today is September 29, 2026. Sending Reminder 1..."
            )
            call_command("send_reminder_1")

        elif today == date(2026, 10, 2):
            self.stdout.write(
                "Today is October 2, 2026. Sending Reminder 2..."
            )
            call_command("send_reminder_2")

        else:
            self.stdout.write(
                f"No SMS reminder is scheduled for {today}."
            )