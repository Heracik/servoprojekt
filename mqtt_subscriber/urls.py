from django.urls import path
from . import views
from .views import send_shutdown_command_view


urlpatterns = [
    path('', views.home, name='home'),
    path('send_time/<str:city>/', views.send_time, name='send_time'),
    path('send_custom_time/', views.send_custom_time, name='send_custom_time'),
    path('send_time/<str:city>/<str:timezone>/', views.send_time_for_city, name='send_time_for_city'),
    path('send_shutdown/', views.send_shutdown_command_view, name='send_shutdown'),
    path('send_sync/', views.send_sync_command_view, name='send_sync'),
    path('send_desync/', views.send_desync_command_view, name='send_desync'),
]
