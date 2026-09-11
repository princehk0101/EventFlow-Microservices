from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")


def health(request):
    return JsonResponse({
        "service": "API Gateway",
        "status": "healthy"
    })


@csrf_exempt
def users(request):

    try:
        data = None

        if request.method == "POST":
            data = json.loads(request.body)

        response = requests.request(
            method=request.method,
            url=USER_SERVICE_URL,
            json=data,
            timeout=5
        )

        return JsonResponse(
            response.json(),
            status=response.status_code,
            safe=False
        )

    except requests.RequestException:
        return JsonResponse(
            {"error": "User Service unavailable"},
            status=503
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )