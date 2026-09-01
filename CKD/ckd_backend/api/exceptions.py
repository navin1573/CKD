from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Provides consistent error responses and logs errors.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the error response
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': get_error_message(response),
            'details': response.data if isinstance(response.data, dict) else str(response.data)
        }

        # Log the error
        logger.error(
            f"API Error: {context['view'].__class__.__name__} - "
            f"Status: {response.status_code} - "
            f"Details: {custom_response_data}"
        )

        response.data = custom_response_data

    return response


def get_error_message(response):
    """Extract meaningful error message from response"""
    if response.status_code == 400:
        return "Bad Request - Invalid input data"
    elif response.status_code == 401:
        return "Unauthorized - Authentication required"
    elif response.status_code == 403:
        return "Forbidden - You don't have permission to access this resource"
    elif response.status_code == 404:
        return "Not Found - The requested resource was not found"
    elif response.status_code == 405:
        return "Method Not Allowed - Invalid HTTP method"
    elif response.status_code == 500:
        return "Internal Server Error - Something went wrong on the server"
    else:
        return "An error occurred"
