# Event RSVP Platform

A Django-based web application for milestone event management, featuring a responsive UI, dynamic countdowns, collapsible text blocks, guest RSVP forms, and an admin guest tracker.

---

## Key Features

* **Interactive Frontend:** Real-time countdown timer, image slideshow gallery, "Read More" text toggle, and confirmation modals.
* **Smart RSVP Handling:** Dynamic guest formsets, phone number prefix validation (`+33`, `+1`), string normalization, and email/phone uniqueness checks.
* **Admin Dashboard:** Real-time sum of total attending guests directly in the Django Admin list header.

---

## Quick Start

### 1. Installation

# Clone repository
git clone [https://github.com/Gavin-Humphrey/event-invitation-platform.git](https://github.com/Gavin-Humphrey/event-invitation-platform.git)
cd event-invitation-platform

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

### 2. Database & Server Setup

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Project Structure
```Plaintext
├── core/
│   ├── models.py      # RSVP & AdditionalGuest models
│   ├── forms.py       # RSVPForm with clean_phone & clean_email validation
│   ├── views.py       # Form and formset processing
│   └── admin.py       # Customized RSVPAdmin with guest aggregation
├── static/
│   └── css/           # Design tokens and styles
├── templates/         # Main HTML templates
├── manage.py
└── README.md
```