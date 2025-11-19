import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import traceback

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware(MiddlewareMixin):
  
    def process_exception(self, request, exception):
        tb = traceback.format_exc()
        logger.error("Unhandled exception at %s\n%s", request.path, tb)
        payload = {
            "success": False,
            "message": "Internal server error",
            "errors": {"detail": ["Internal server error"]},
        }
        if settings.DEBUG:
            payload["errors"]["traceback"] = [tb]
            payload["message"] = str(exception)
        return JsonResponse(payload, status=500)
