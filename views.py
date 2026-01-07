import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from models import Task

# Helper to parse JSON body
def parse_body(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def register_view(request):
    if request.method == 'GET':
        return HttpResponse("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Register - Task Manager</title>
                <style>
                    body {
                        background-color: #f0f2f5; /* 60% Primary Background */
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .card {
                        background-color: #ffffff; /* 30% Secondary Container */
                        padding: 2.5rem;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 400px;
                        text-align: center;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 1.5rem;
                        font-weight: 600;
                    }
                    input {
                        width: 100%;
                        padding: 12px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        box-sizing: border-box;
                        font-size: 16px;
                        transition: border-color 0.3s;
                    }
                    input:focus {
                        border-color: #5c6bc0;
                        outline: none;
                    }
                    button {
                        width: 100%;
                        background-color: #5c6bc0; /* 10% Accent Color */
                        color: white;
                        padding: 14px;
                        margin-top: 1rem;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 600;
                        transition: background-color 0.3s;
                    }
                    button:hover {
                        background-color: #3f51b5;
                    }
                    .link {
                        margin-top: 1.5rem;
                        font-size: 0.9rem;
                        color: #666;
                    }
                    .link a {
                        color: #5c6bc0;
                        text-decoration: none;
                        font-weight: 600;
                    }
                    .link a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Create Account</h1>
                    <form id="registerForm">
                        <input type="text" id="username" placeholder="Username" required>
                        <input type="password" id="password" placeholder="Password" required>
                        <button type="submit">Sign Up</button>
                    </form>
                    <div class="link">
                        Already have an account? <a href="/login/">Log In</a>
                    </div>
                </div>
                <script>
                    function getCookie(name) {
                        let cookieValue = null;
                        if (document.cookie && document.cookie !== '') {
                            const cookies = document.cookie.split(';');
                            for (let i = 0; i < cookies.length; i++) {
                                const cookie = cookies[i].trim();
                                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }
                            }
                        }
                        return cookieValue;
                    }
                    document.getElementById('registerForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const username = document.getElementById('username').value;
                        const password = document.getElementById('password').value;
                        const response = await fetch('/register/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({username, password})
                        });
                        const result = await response.json();
                        if(response.ok) {
                            window.location.href = '/login/';
                        } else {
                            alert(result.message || 'Error');
                        }
                    });
                </script>
            </body>
            </html>
        """)

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

@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def login_view(request):
    if request.method == 'GET':
        return HttpResponse("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login - Task Manager</title>
                <style>
                    body {
                        background-color: #f0f2f5;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .card {
                        background-color: #ffffff;
                        padding: 2.5rem;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 400px;
                        text-align: center;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 1.5rem;
                        font-weight: 600;
                    }
                    input {
                        width: 100%;
                        padding: 12px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        box-sizing: border-box;
                        font-size: 16px;
                        transition: border-color 0.3s;
                    }
                    input:focus {
                        border-color: #5c6bc0;
                        outline: none;
                    }
                    button {
                        width: 100%;
                        background-color: #5c6bc0;
                        color: white;
                        padding: 14px;
                        margin-top: 1rem;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 600;
                        transition: background-color 0.3s;
                    }
                    button:hover {
                        background-color: #3f51b5;
                    }
                    .link {
                        margin-top: 1.5rem;
                        font-size: 0.9rem;
                        color: #666;
                    }
                    .link a {
                        color: #5c6bc0;
                        text-decoration: none;
                        font-weight: 600;
                    }
                    .link a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Welcome Back</h1>
                    <form id="loginForm">
                        <input type="text" id="username" placeholder="Username" required>
                        <input type="password" id="password" placeholder="Password" required>
                        <button type="submit">Log In</button>
                    </form>
                    <div class="link">
                        Don't have an account? <a href="/register/">Sign Up</a>
                    </div>
                </div>
                <script>
                    function getCookie(name) {
                        let cookieValue = null;
                        if (document.cookie && document.cookie !== '') {
                            const cookies = document.cookie.split(';');
                            for (let i = 0; i < cookies.length; i++) {
                                const cookie = cookies[i].trim();
                                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }
                            }
                        }
                        return cookieValue;
                    }
                    document.getElementById('loginForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const username = document.getElementById('username').value;
                        const password = document.getElementById('password').value;
                        const response = await fetch('/login/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({username, password})
                        });
                        const result = await response.json();
                        if(response.ok) {
                            // Redirect to dashboard or home on success
                            alert('Login successful!');
                            // window.location.href = '/dashboard/'; 
                        } else {
                            alert(result.message || 'Error');
                        }
                    });
                </script>
            </body>
            </html>
        """)

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