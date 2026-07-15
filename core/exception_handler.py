from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred."

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = response.data["detail"]
            else:
                first_error = next(iter(response.data.values()))
                if isinstance(first_error, list):
                    message = first_error[0]
                else:
                    message = first_error

        response.data = {
            "success": False,
            "status": response.status_code,
            "message": str(message),
            "data": None,
        }

    return response