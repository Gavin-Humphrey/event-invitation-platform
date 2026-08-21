from django.contrib import admin
from .models import Event, RSVP, AdditionalGuest
from django.db.models import Sum


class AdditionalGuestInline(admin.TabularInline):
    model = AdditionalGuest
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue_name', 'rsvp_deadline')


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = (
        'suffix',
        'full_name', 
        'email', 
        'phone', 
        'attending', 
        'guest_count', 
        'additional_guests_list',
        'dietary_requirements', 
        'short_message', 
        'created_at',
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

    # ###
    def changelist_view(self, request, extra_context=None):
            extra_context = extra_context or {}
    
            # 1. Sum guest_count where attending == 'YES'
            total_attending_guests = (
                RSVP.objects.filter(attending='YES').aggregate(
                    total=Sum('guest_count')
                )['total']
                or 0
            )
    
            # 2. Count total primary RSVPs who said YES vs NO
            total_yes_rsvps = RSVP.objects.filter(attending='YES').count()
            total_no_rsvps = RSVP.objects.filter(attending='NO').count()
    
            # Inject into admin context banner
            extra_context['title'] = (
                f"Select RSVP to change | TOTAL ATTENDING GUESTS: {total_attending_guests} "
                f"({total_yes_rsvps} RSVPs Accepted, {total_no_rsvps} Declined)"
            )
    
            return super().changelist_view(request, extra_context=extra_context)
    # ######

@admin.register(AdditionalGuest)
class AdditionalGuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rsvp')
    search_fields = ('full_name',)