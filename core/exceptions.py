"""
Custom DRF exception handler.
Wraps all API error responses in a consistent JSON envelope:
{
    "error": {
        "message": "...",
        "details": ...   # optional, only present for validation errors
    }
}
"""

import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # An unhandled exception (e.g. a bug) — DRF didn't produce a response.
        # Log it with full context so it's traceable, and return a generic 500
        # rather than leaking a raw traceback to the client.
        logger.exception(
            "Unhandled exception in API view",
            extra={
                "view": (
                    context.get("view").__class__.__name__
                    if context.get("view")
                    else None
                )
            },
        )
        return None  # let Django's default 500 handling take over

    error_message = "An error occurred."
    details = None

    if isinstance(response.data, dict):
        if "detail" in response.data:
            error_message = str(response.data["detail"])
        else:
            # Likely a validation error: {"field_name": ["error1", "error2"]}
            error_message = "Validation failed."
            details = response.data
    elif isinstance(response.data, list):
        error_message = "Validation failed."
        details = response.data

    logger.warning(
        "API error response",
        extra={"status_code": response.status_code, "error_message": error_message},
    )

    response.data = {"error": {"message": error_message, "details": details}}
    return response
