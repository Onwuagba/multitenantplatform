from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Success"):
    """Standard success response format"""
    return Response({
        'status': 'success',
        'message': message,
        'data': data
    })

def error_response(error, status_code=status.HTTP_400_BAD_REQUEST, data=None):
    """Standard error response format"""
    return Response({
        'status': 'failure',
        'error': error,
        'data': data
    }, status=status_code)