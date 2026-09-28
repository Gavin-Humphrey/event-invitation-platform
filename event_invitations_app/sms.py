# import logging

# import requests
# from django.conf import settings
# from .models import RSVP


# logger = logging.getLogger(__name__)


# PURESMS_BULK_URL = "https://connect-api.divergent.cloud/sms/send/bulk"


# def send_sms_batch(messages, send_at_utc=None):
#     """
#     Send a batch of SMS messages through PureSMS.

#     messages should be a list like:
#     [
#         {
#             "recipient": "+447700900123",
#             "content": "Your reminder message..."
#         }
#     ]

#     send_at_utc is optional. If provided, PureSMS schedules the batch.
#     """

#     if not settings.PURESMS_API_KEY:
#         logger.warning("PureSMS API key is not configured.")
#         return False

#     if not messages:
#         logger.warning("No SMS messages to send.")
#         return False

#     payload_messages = []

#     for message in messages:
#         payload_messages.append({
#             "sender": settings.PURESMS_SENDER,
#             "recipient": message["recipient"],
#             "content": message["content"],
#         })

#     payload = {
#         "messages": payload_messages,
#     }

#     if send_at_utc:
#         payload["sendAtUtc"] = send_at_utc

#     headers = {
#         "X-Api-Key": settings.PURESMS_API_KEY,
#         "Content-Type": "application/json",
#     }

#     try:
#         response = requests.post(
#             PURESMS_BULK_URL,
#             headers=headers,
#             json=payload,
#             timeout=10,
#         )

#         if response.ok:
#             logger.info(
#                 "PureSMS batch accepted successfully. "
#                 "Messages: %s",
#                 len(payload_messages),
#             )
#             return True

#         logger.error(
#             "PureSMS batch failed: %s - %s",
#             response.status_code,
#             response.text,
#         )
#         return False

#     except requests.RequestException as exc:
#         logger.exception("PureSMS batch request failed: %s", exc)
#         return False


# # def send_test_reminder():
# #     """
# #     Send a test reminder SMS to the verified PureSMS test number.
# #     """

# #     messages = [
# #         {
# #             "recipient": "+447537141203",
# #             "content": (
# #                 "Chief Jerry's 80th Birthday: "
# #                 "This is a test reminder. "
# #                 "To see if the SMS system is working."
# #             ),
# #         }
# #     ]

# #     return send_sms_batch(messages)


# def schedule_rsvp_reminders():
#     """
#     Schedule the two SMS reminders for all confirmed RSVPs.
#     """

#     confirmed_rsvps = RSVP.objects.filter(
#         attending=RSVP.AttendingStatus.YES
#     ).exclude(
#         phone=""
#     )

#     # Reminder 1 — September 29 at 6:00 PM UK
#     reminder_1 = (
#         "Good evening 😊 We're so excited and looking forward to seeing you "
#         "and celebrating this very special milestone — Chief Jerry "
#         "Chukwuemeka Aguiyi's 80th birthday! 🎉 "
#         "A little reminder to please come early so you don't miss any part "
#         "of the celebration. The party starts promptly at 5:00 PM — "
#         "please, no African time o! 😄 "
#         "📍 Prince Regent Hotel, Manor Road, Woodford, Chigwell, "
#         "Essex, IG8 8AE "
#         "We can't wait to celebrate together. See you soon! 🎉"
#     )

#     # Reminder 2 — October 2 at 6:00 PM UK
#     reminder_2 = (
#         "Good evening 😊 Just one last reminder that Chief Jerry "
#         "Chukwuemeka Aguiyi's 80th birthday celebration is tomorrow! 🎉 "
#         "The party starts promptly at 5:00 PM, so please come early — "
#         "no African time o! 😄 "
#         "📍 Prince Regent Hotel, Manor Road, Woodford, Chigwell, "
#         "Essex, IG8 8AE "
#         "We can't wait to celebrate with you. See you tomorrow! 🎉"
#     )

#     messages_1 = [
#         {
#             "recipient": rsvp.phone,
#             "content": reminder_1,
#         }
#         for rsvp in confirmed_rsvps
#     ]

#     messages_2 = [
#         {
#             "recipient": rsvp.phone,
#             "content": reminder_2,
#         }
#         for rsvp in confirmed_rsvps
#     ]

#     results = {
#         "reminder_1": send_sms_batch(
#             messages_1,
#             send_at_utc="2026-09-29T17:00:00Z",
#         ),
#         "reminder_2": send_sms_batch(
#             messages_2,
#             send_at_utc="2026-10-02T17:00:00Z",
#         ),
#         "recipient_count": confirmed_rsvps.count(),
#     }

#     return results


import logging

import requests
from django.conf import settings
from .models import RSVP


logger = logging.getLogger(__name__)


CLICKSEND_SMS_URL = "https://rest.clicksend.com/v3/sms/send"


def send_sms_batch(messages):
    """
    Send a batch of SMS messages through ClickSend.

    messages should be a list like:
    [
        {
            "recipient": "+447700900123",
            "content": "Your reminder message..."
        }
    ]
    """

    if not settings.CLICKSEND_USERNAME:
        logger.warning("ClickSend username is not configured.")
        return False

    if not settings.CLICKSEND_API_KEY:
        logger.warning("ClickSend API key is not configured.")
        return False

    if not messages:
        logger.warning("No SMS messages to send.")
        return False

    payload = {
        "messages": [
            {
                "to": message["recipient"],
                "body": message["content"],
            }
            for message in messages
        ]
    }

    try:
        response = requests.post(
            CLICKSEND_SMS_URL,
            auth=(
                settings.CLICKSEND_USERNAME,
                settings.CLICKSEND_API_KEY,
            ),
            json=payload,
            timeout=10,
        )

        if response.ok:
            logger.info(
                "ClickSend batch accepted successfully. Messages: %s",
                len(messages),
            )
            logger.info("ClickSend response: %s", response.text)
            return True

        logger.error(
            "ClickSend batch failed: %s - %s",
            response.status_code,
            response.text,
        )
        return False

    except requests.RequestException as exc:
        logger.exception("ClickSend batch request failed: %s", exc)
        return False


def schedule_rsvp_reminders():
    """
    Prepare the two SMS reminders for all confirmed RSVPs.
    """

    confirmed_rsvps = RSVP.objects.filter(
        attending=RSVP.AttendingStatus.YES
    ).exclude(
        phone=""
    )

    reminder_1 = (
        "Good evening 😊 We're so excited and looking forward to seeing you "
        "and celebrating this very special milestone — Chief Jerry "
        "Chukwuemeka Aguiyi's 80th birthday! 🎉 "
        "A little reminder to please come early so you don't miss any part "
        "of the celebration. The party starts promptly at 5:00 PM — "
        "please, no African time o! 😄 "
        "📍 Prince Regent Hotel, Manor Road, Woodford, Chigwell, "
        "Essex, IG8 8AE "
        "We can't wait to celebrate together. See you soon! 🎉"
    )

    reminder_2 = (
        "Good evening 😊 Just one last reminder that Chief Jerry "
        "Chukwuemeka Aguiyi's 80th birthday celebration is tomorrow! 🎉 "
        "The party starts promptly at 5:00 PM, so please come early — "
        "no African time o! 😄 "
        "📍 Prince Regent Hotel, Manor Road, Woodford, Chigwell, "
        "Essex, IG8 8AE "
        "We can't wait to celebrate with you. See you tomorrow! 🎉"
    )

    messages_1 = [
        {
            "recipient": rsvp.phone,
            "content": reminder_1,
        }
        for rsvp in confirmed_rsvps
    ]

    messages_2 = [
        {
            "recipient": rsvp.phone,
            "content": reminder_2,
        }
        for rsvp in confirmed_rsvps
    ]

    return {
        "reminder_1": messages_1,
        "reminder_2": messages_2,
        "recipient_count": confirmed_rsvps.count(),
    }