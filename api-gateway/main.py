import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://user-service:8000"
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "api-gateway"
    }


@app.api_route(
    "/users/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def users_proxy(request: Request, path: str):

    # User Service ka actual endpoint /api/users/ hai
    if path:
        url = f"{USER_SERVICE_URL}/api/users/{path}"
    else:
        url = f"{USER_SERVICE_URL}/api/users/"

    body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:

        response = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers=headers,
            params=request.query_params,
        )

    content_type = response.headers.get("content-type", "")

    if "application/json" in content_type:
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=content_type or "text/plain"
    )