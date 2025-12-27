from django.db import models

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']

class ContactMessage(models.Model):
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.email} at {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']

class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.subject} - {self.sent_at}"
    
    class Meta:
        ordering = ['-sent_at']