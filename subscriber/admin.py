from django.contrib import admin
from .models import NewsletterSubscriber, ContactMessage


admin.site.register(NewsletterSubscriber)
admin.site.register(ContactMessage)