
from django.contrib import admin
from django.urls import path
from subscriber.views import subscribe_newsletter, contact

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/contact/', contact, name='contact'),
    path('api/subscribe/', subscribe_newsletter, name='subscribe'),
    
]
