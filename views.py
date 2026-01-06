import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from .models import Task

# Helper to parse JSON body
def parse_body(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

@require_http_methods(["POST"])
def register_view(request):
    data = parse_body(request)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return JsonResponse({'status': 'fail', 'message': 'Username and password required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'status': 'fail', 'message': 'Username already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password)
    login(request, user) # Auto login
    
    return JsonResponse({'status': 'success', 'data': {'user': {'username': user.username}}}, status=201)

@require_http_methods(["POST"])
def login_view(request):
    data = parse_body(request)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'status': 'success', 'data': {'user': {'username': user.username}}})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Incorrect username or password'}, status=401)

def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})

@require_http_methods(["GET", "POST"])
def task_list_create_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)

    if request.method == 'GET':
        # Return tasks as list of dicts
        tasks = list(Task.objects.filter(user=request.user).values('id', 'title', 'status', 'priority', 'description'))
        return JsonResponse({'status': 'success', 'data': {'tasks': tasks}})

    if request.method == 'POST':
        data = parse_body(request)
        task = Task.objects.create(
            user=request.user,
            title=data.get('title'),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'pending')
        )
        return JsonResponse({'status': 'success', 'data': {'task': {
            'id': task.id, 'title': task.title, 'priority': task.priority
        }}}, status=201)

@require_http_methods(["DELETE"])
def task_detail_view(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)

    try:
        # Admin (is_staff) can delete any task, regular users only their own
        if request.user.is_staff:
            task = Task.objects.get(pk=pk)
        else:
            task = Task.objects.get(pk=pk, user=request.user)
        
        task.delete()
        return JsonResponse({'status': 'success'}, status=204)
    except Task.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Task not found'}, status=404)