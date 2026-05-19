from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('booking/new/', views.booking_create, name='booking_create'),
    path('halls/', views.halls, name='halls'),
    path('halls/<int:room_id>/availability/', views.hall_availability, name='hall_availability'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]
