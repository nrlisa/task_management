import jwt
import os
from django.http import JsonResponse
from django.conf import settings
from functools import wraps

# Helper to get the secret key
def get_jwt_secret():
    return os.environ.get('JWT_SECRET', getattr(settings, 'SECRET_KEY', 'fallback-secret'))

class JWTAuthenticationMiddleware:
    """
    Middleware to verify JWT tokens on incoming requests.
    Replaces: authenticateUser in auth.js
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                secret = get_jwt_secret()
                # Verify token
                payload = jwt.decode(token, secret, algorithms=['HS256'])
                # Attach user data to request (similar to req.user = verified in JS)
                request.jwt_user = payload
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid Token'}, status=400)
        
        return self.get_response(request)

def require_role(role):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Replaces: requireRole in auth.js
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user data exists (set by middleware) and matches role
            if not hasattr(request, 'jwt_user'):
                 return JsonResponse({'error': 'Access Denied: No token provided.'}, status=401)
            
            if request.jwt_user.get('role') != role:
                 return JsonResponse({'error': 'Access Denied: Insufficient permissions.'}, status=403)
                 
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator