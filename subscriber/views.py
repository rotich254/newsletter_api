from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import NewsletterSubscriber

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
        return JsonResponse({"status": "success", "message": "Subscription successful!"}, status=201)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)



@csrf_exempt
def contact(request):
    if request.method == "OPTIONS":
        return JsonResponse({"status": "ok"}, status=200)
    
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        email = data.get("email")
        message = data.get("message")

        # LOG TO TERMINAL
        print("📩 New contact message received:")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print("-" * 50)

        return JsonResponse({"message": "Message sent successfully!"}, status=201)

    return JsonResponse({"message": "POST only"}, status=405)

        
        
    

        
                         
