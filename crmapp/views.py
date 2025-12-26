from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )
        if user:
            return JsonResponse({"message": "Login success"})
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    return JsonResponse({"message": "Use POST method"})


