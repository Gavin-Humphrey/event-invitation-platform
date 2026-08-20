from django.contrib import admin
from .models import Event, RSVP, AdditionalGuest


class AdditionalGuestInline(admin.TabularInline):
    model = AdditionalGuest
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue_name', 'rsvp_deadline')


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 
        'email', 
        'phone', 
        'attending', 
        'guest_count', 
        'additional_guests_list',
        'dietary_requirements', 
        'short_message', 
        'created_at'
    )
    list_filter = ('attending', 'guest_count')
    search_fields = ('full_name', 'email', 'phone', 'dietary_requirements', 'message')
    inlines = [AdditionalGuestInline]

    fieldsets = (
        ('Guest Details', {
            'fields': ('event', 'full_name', 'email', 'phone', 'attending', 'guest_count')
        }),
        ('Additional Information', {
            'fields': ('dietary_requirements', 'message')
        }),
    )

    @admin.display(description='Accompanying Guests')
    def additional_guests_list(self, obj):
        # Gracefully handle custom related_name or default reverse relationship
        related_mgr = getattr(obj, 'additional_guests', getattr(obj, 'additionalguest_set', None))
        if related_mgr:
            guests = related_mgr.all()
            if guests:
                return ", ".join([g.full_name for g in guests])
        return "-"

    @admin.display(description='Special Message')
    def short_message(self, obj):
        if obj.message and len(obj.message) > 40:
            return f"{obj.message[:40]}..."
        return obj.message or "-"


@admin.register(AdditionalGuest)
class AdditionalGuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rsvp')
    search_fields = ('full_name',)