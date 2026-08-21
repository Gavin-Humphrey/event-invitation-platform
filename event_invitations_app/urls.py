from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/rsvp/<int:pk>/', views.view_rsvp, name='view_rsvp'),
    path('dashboard/rsvp/<int:pk>/edit/', views.edit_rsvp, name='edit_rsvp'),
    path('dashboard/gallery/<int:pk>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
]