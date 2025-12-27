from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import NewsletterSubscriber
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@csrf_exempt
def health_check(request):
    """Health check endpoint for server monitoring"""
    return JsonResponse({
        "status": "ok",
        "service": "Newsletter API",
        "version": "1.0.0"
    }, status=200)


@csrf_exempt
def subscribe_newsletter(request):
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get("email")
        except (json.JSONDecodeError, AttributeError):
            email = request.POST.get("email")

        if not email:
            return JsonResponse({"status": "error", "message": "Email is required"}, status=400)
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already subscribed"}, status=400)
        NewsletterSubscriber.objects.create(email=email)
        subscriber_subject = "Thank you for subscribing!"
        subscriber_message = (
            f"Hi there!\n\n"
            f"Thank you for subscribing to our newsletter!\n"
            f"You'll now receive updates, new features, and special offers.\n\n"
            f"Warm regards,\n"
            f"softwizpro.com"
        )

        send_mail(
            subscriber_subject,
            subscriber_message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        admin_email = "rotichk254@gmail.com"  
        admin_subject = "New Newsletter Subscriber"
        admin_message = f"A new user subscribed to the newsletter:\n\nEmail: {email}"

        send_mail(
            admin_subject,
            admin_message,
            settings.EMAIL_HOST_USER,
            [admin_email],
            fail_silently=True,
        )

        return JsonResponse(
            {"status": "success", "message": "Subscription successful! Email sent."},
            status=201
        )

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@csrf_exempt
def contact(request):
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        email = data.get("email")
        message = data.get("message")

        # Save to database
        from .models import ContactMessage
        ContactMessage.objects.create(email=email, message=message)

        # LOG TO TERMINAL
        print("📩 New contact message received:")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print("-" * 50)

        return JsonResponse({"message": "Message sent successfully!"}, status=201)

    return JsonResponse({"message": "POST only"}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscribers(request):
    """Get all subscribers with pagination and search (requires authentication)"""
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "GET":
        from django.core.paginator import Paginator
        
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        subscribers = NewsletterSubscriber.objects.all()
        
        if search:
            subscribers = subscribers.filter(email__icontains=search)
        
        paginator = Paginator(subscribers, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            "subscribers": [
                {
                    "id": sub.id,
                    "email": sub.email,
                    "subscribed_at": sub.subscribed_at.isoformat(),
                    "is_active": sub.is_active
                }
                for sub in page_obj
            ],
            "total": paginator.count,
            "page": page,
            "pages": paginator.num_pages,
            "per_page": per_page
        }
        
        return JsonResponse(data, status=200)
    
    return JsonResponse({"message": "GET only"}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscriber_stats(request):
    """Get subscriber statistics for dashboard (requires authentication)"""
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "GET":
        from django.utils import timezone
        from datetime import timedelta
        
        total = NewsletterSubscriber.objects.filter(is_active=True).count()
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        new_today = NewsletterSubscriber.objects.filter(
            subscribed_at__date=today
        ).count()
        
        new_this_week = NewsletterSubscriber.objects.filter(
            subscribed_at__date__gte=week_ago
        ).count()
        
        data = {
            "total_subscribers": total,
            "new_today": new_today,
            "new_this_week": new_this_week
        }
        
        return JsonResponse(data, status=200)
    
    return JsonResponse({"message": "GET only"}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get all contact messages with pagination (requires authentication)"""
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "GET":
        from django.core.paginator import Paginator
        from .models import ContactMessage
        
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        unread_only = request.GET.get('unread', 'false') == 'true'
        
        messages = ContactMessage.objects.all()
        
        if unread_only:
            messages = messages.filter(is_read=False)
        
        paginator = Paginator(messages, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            "messages": [
                {
                    "id": msg.id,
                    "email": msg.email,
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat(),
                    "is_read": msg.is_read
                }
                for msg in page_obj
            ],
            "total": paginator.count,
            "unread_count": ContactMessage.objects.filter(is_read=False).count(),
            "page": page,
            "pages": paginator.num_pages,
            "per_page": per_page
        }
        
        return JsonResponse(data, status=200)
    
    return JsonResponse({"message": "GET only"}, status=405)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_read(request, message_id):
    """Mark a message as read (requires authentication)"""
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "POST":
        from .models import ContactMessage
        
        try:
            message = ContactMessage.objects.get(id=message_id)
            message.is_read = True
            message.save()
            return JsonResponse({"status": "success", "message": "Message marked as read"}, status=200)
        except ContactMessage.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Message not found"}, status=404)
    
    return JsonResponse({"message": "POST only"}, status=405)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_newsletter(request):
    """Send newsletter to all active subscribers (requires authentication)"""
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "POST":
        from .models import Newsletter
        
        data = json.loads(request.body.decode("utf-8"))
        subject = data.get("subject")
        content = data.get("content")
        
        if not subject or not content:
            return JsonResponse({"status": "error", "message": "Subject and content are required"}, status=400)
        
        # Get all active subscribers
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        recipient_emails = [sub.email for sub in subscribers]
        
        if not recipient_emails:
            return JsonResponse({"status": "error", "message": "No active subscribers"}, status=400)
        
        # Send emails
        try:
            for email in recipient_emails:
                send_mail(
                    subject,
                    content,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=True,
                )
            
            # Save newsletter record
            newsletter = Newsletter.objects.create(
                subject=subject,
                content=content,
                recipients_count=len(recipient_emails)
            )
            
            return JsonResponse({
                "status": "success",
                "message": f"Newsletter sent to {len(recipient_emails)} subscribers",
                "recipients_count": len(recipient_emails)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"message": "POST only"}, status=405)
