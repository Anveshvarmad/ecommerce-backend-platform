from audit.models import AuditLog


class AuditLogMiddleware:
    """
    Logs write operations for operational visibility.

    It intentionally logs only metadata, not full request bodies,
    so sensitive payloads like passwords and tokens are not stored.
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            if self.should_log(request):
                AuditLog.objects.create(
                    actor=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                    action=self.infer_action(request),
                    method=request.method,
                    path=request.path[:500],
                    status_code=getattr(response, "status_code", 0),
                    resource_type=self.infer_resource_type(request),
                    resource_id=self.infer_resource_id(request),
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
                    correlation_id=getattr(request, "correlation_id", ""),
                    metadata={
                        "query_string": request.META.get("QUERY_STRING", ""),
                        "content_type": request.META.get("CONTENT_TYPE", ""),
                    },
                )
        except Exception:
            pass

        return response

    def should_log(self, request):
        if request.method not in self.WRITE_METHODS:
            return False

        ignored_prefixes = [
            "/admin/jsi18n/",
            "/api/health/",
        ]

        return not any(request.path.startswith(prefix) for prefix in ignored_prefixes)

    def infer_action(self, request):
        path = request.path.lower()

        if "checkout" in path:
            return AuditLog.Action.CHECKOUT

        if "payments" in path:
            return AuditLog.Action.PAYMENT

        if "status" in path:
            return AuditLog.Action.STATUS_CHANGE

        if "auth" in path:
            return AuditLog.Action.AUTH

        if request.method == "POST":
            return AuditLog.Action.CREATE

        if request.method in ["PUT", "PATCH"]:
            return AuditLog.Action.UPDATE

        if request.method == "DELETE":
            return AuditLog.Action.DELETE

        return AuditLog.Action.OTHER

    def infer_resource_type(self, request):
        path = request.path.lower()

        if "/api/catalog/products" in path:
            return "product"

        if "/api/catalog/categories" in path:
            return "category"

        if "/api/cart" in path:
            return "cart"

        if "/api/orders" in path:
            return "order"

        if "/api/payments" in path:
            return "payment"

        if "/api/backoffice" in path:
            return "backoffice"

        if "/api/auth" in path:
            return "auth"

        return "unknown"

    def infer_resource_id(self, request):
        parts = [part for part in request.path.strip("/").split("/") if part.isdigit()]
        return parts[-1] if parts else ""

    def get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")
