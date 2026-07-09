import uuid


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.correlation_id = correlation_id

        response = self.get_response(request)
        response["X-Request-ID"] = correlation_id

        return response
