
from django.contrib import admin
from django.urls import path
from subscriber.views import (
    health_check,
    subscribe_newsletter, 
    contact,
    get_subscribers,
    get_subscriber_stats,
    get_messages,
    mark_message_read,
    send_newsletter
)
from subscriber.authentication import (
    login_view,
    current_user,
    logout_view
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    
    # Public endpoints
    path('api/contact/', contact, name='contact'),
    path('api/subscribe/', subscribe_newsletter, name='subscribe'),
    
    # Authentication endpoints
    path('api/admin/login/', login_view, name='admin_login'),
    path('api/admin/logout/', logout_view, name='admin_logout'),
    path('api/admin/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/admin/me/', current_user, name='current_user'),
    
    # Admin API endpoints (protected)
    path('api/subscribers/', get_subscribers, name='get_subscribers'),
    path('api/subscribers/stats/', get_subscriber_stats, name='get_subscriber_stats'),
    path('api/messages/', get_messages, name='get_messages'),
    path('api/messages/<int:message_id>/read/', mark_message_read, name='mark_message_read'),
    path('api/newsletter/send/', send_newsletter, name='send_newsletter'),
]
