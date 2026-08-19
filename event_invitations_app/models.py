from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200, default="Chief Jerry's 80th Birthday")
    event_date = models.DateTimeField()
    venue_name = models.CharField(max_length=200)
    address = models.TextField()
    dress_code = models.CharField(max_length=100)
    rsvp_deadline = models.DateField()
    about_text = models.TextField()

    def __str__(self):
        return self.title