import json
import re
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.core.cache import cache
from .models import Task

# Mass Assignment Protect: Define allowed fields for updates
FILLABLE_FIELDS = ['title', 'description', 'priority', 'status', 'due_date']

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

    # Input Validation: Whitelist/Regex for username
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return JsonResponse({'status': 'fail', 'message': 'Username can only '
        'contain letters, numbers, and underscores'}, status=400)

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
                    <h1>Welcome Back To</h1>
                <h1>Task Management</h1>
                            
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
                            if (result.data.user.is_staff) {
                                window.location.href = '/secure-admin-portal/';
                            } else {
                                window.location.href = '/dashboard/';
                            }
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

    # Brute-Force Protection: Check failed attempts
    ip = request.META.get('REMOTE_ADDR')
    lockout_key = f"login_failed_{ip}"
    attempts = cache.get(lockout_key, 0)

    if attempts >= 5:
        return JsonResponse({'status': 'fail', 'message': 'Too many failed attempts. Please try again in 5 minutes.'}, status=429)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Reset failed attempts on success
        cache.delete(lockout_key)
        login(request, user)
        return JsonResponse({'status': 'success', 'data': {'user': {'username': user.username, 'is_staff': user.is_staff}}})
    else:
        # Increment failed attempts and set timeout (300 seconds = 5 minutes)
        cache.set(lockout_key, attempts + 1, timeout=300)
        return JsonResponse({'status': 'fail', 'message': 'Incorrect username or password'}, status=401)

def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})

@login_required(login_url='/login/')
@ensure_csrf_cookie
def dashboard_view(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - Task Manager</title>
            <style>
                body {
                    background-color: #f0f2f5;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #ffffff;
                    padding: 1rem 2rem;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    margin-bottom: 2rem;
                }
                .navbar h1 { margin: 0; color: #333; font-size: 1.5rem; }
                .btn-logout {
                    background-color: #ff5252;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                }
                .card {
                    background-color: #ffffff;
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    margin-bottom: 2rem;
                }
                .form-group { margin-bottom: 1rem; }
                input, select, textarea {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    box-sizing: border-box;
                    font-family: inherit;
                }
                button.primary {
                    background-color: #5c6bc0;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                    width: 100%;
                }
                button.primary:hover { background-color: #3f51b5; }
                .task-item {
                    background-color: #fff;
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .task-info h3 { margin: 0 0 0.5rem 0; color: #333; }
                .task-meta { font-size: 0.85rem; color: #666; }
                .badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    margin-right: 8px;
                }
                .badge-high { background-color: #ffebee; color: #c62828; }
                .badge-medium { background-color: #fff3e0; color: #ef6c00; }
                .badge-low { background-color: #e8f5e9; color: #2e7d32; }
                .actions button {
                    margin-left: 8px;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9rem;
                }
                .btn-edit { background-color: #e3f2fd; color: #1565c0; }
                .btn-delete { background-color: #ffebee; color: #c62828; }
                
                /* Colorful Dropdowns */
                select { font-weight: 600; cursor: pointer; transition: all 0.3s ease; }
                select#priority.Low { background-color: #e8f5e9; color: #2e7d32; border-color: #2e7d32; }
                select#priority.Medium { background-color: #fff3e0; color: #ef6c00; border-color: #ef6c00; }
                select#priority.High { background-color: #ffebee; color: #c62828; border-color: #c62828; }

                select#status.pending { background-color: #f5f5f5; color: #616161; border-color: #9e9e9e; }
                select#status.in-progress { background-color: #e3f2fd; color: #1976d2; border-color: #1976d2; }
                select#status.completed { background-color: #e8f5e9; color: #388e3c; border-color: #388e3c; }
            </style>
        </head>
        <body>
            <div class="navbar">
                <h1>Task Dashboard</h1>
                <button class="btn-logout" onclick="logout()">Logout</button>
            </div>
            <div class="container">
                <div class="card">
                    <h2 id="formTitle">Add New Task</h2>
                    <form id="taskForm">
                        <input type="hidden" id="taskId">
                        <div class="form-group">
                            <input type="text" id="title" placeholder="Task Title" required>
                        </div>
                        <div class="form-group">
                            <textarea id="description" placeholder="Description (optional)" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="due_date" style="display:block; margin-bottom:5px; color:#666; font-weight:600; font-size:0.9rem;">Due Date</label>
                            <input type="date" id="due_date">
                        </div>
                        <div class="form-group" style="display: flex; gap: 10px;">
                            <select id="priority" onchange="updateSelectColor(this)">
                                <option value="Low">Low Priority</option>
                                <option value="Medium" selected>Medium Priority</option>
                                <option value="High">High Priority</option>
                            </select>
                            <select id="status" onchange="updateSelectColor(this)">
                                <option value="pending">Pending</option>
                                <option value="in-progress">In Progress</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>
                        <button type="submit" class="primary" id="submitBtn">Create Task</button>
                        <button type="button" id="cancelBtn" style="display:none; margin-top:10px; background:#eee; color:#333; width:100%; padding:10px; border:none; border-radius:6px; cursor:pointer;">Cancel Edit</button>
                    </form>
                </div>
                <div id="taskList">
                    <!-- Tasks will be loaded here -->
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

                const csrfToken = getCookie('csrftoken');
                let tasksMap = {};

                async function loadTasks() {
                    const response = await fetch('/api/tasks/');
                    const result = await response.json();
                    const list = document.getElementById('taskList');
                    list.innerHTML = '';
                    tasksMap = {};
                    if (result.data && result.data.tasks) {
                        result.data.tasks.forEach(task => {
                            tasksMap[task.id] = task;
                            const div = document.createElement('div');
                            div.className = 'task-item';
                            div.innerHTML = `
                                <div class="task-info">
                                    <h3>${escapeHtml(task.title)}</h3>
                                    <div class="task-meta">
                                        <span class="badge badge-${escapeAttr(task.priority).toLowerCase()}">${escapeHtml(task.priority)}</span>
                                        <span class="badge" style="background:#f5f5f5; color:#666;">${escapeHtml(task.status)}</span>
                                        ${task.due_date ? `<span class="badge" style="background:#e3f2fd; color:#1565c0;">Due: ${escapeHtml(task.due_date)}</span>` : ''}
                                        <p>${escapeHtml(task.description || '')}</p>
                                    </div>
                                </div>
                                <div class="actions">
                                    <button class="btn-edit" onclick="editTask(${task.id})">Edit</button>
                                    <button class="btn-delete" onclick="deleteTask(${task.id})">Delete</button>
                                </div>
                            `;
                            list.appendChild(div);
                        });
                    }
                }

                // Context-specific encoding: HTML Body
                function escapeHtml(text) {
                    if (!text) return '';
                    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                }

                // Context-specific encoding: HTML Attributes
                function escapeAttr(text) {
                    if (!text) return '';
                    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
                }

                async function deleteTask(id) {
                    if(!confirm('Are you sure?')) return;
                    await fetch(`/api/tasks/${id}/`, {
                        method: 'DELETE',
                        headers: {'X-CSRFToken': csrfToken}
                    });
                    loadTasks();
                }

                function updateSelectColor(select) {
                    select.className = select.value;
                }

                window.editTask = function(id) {
                    const task = tasksMap[id];
                    if (!task) return;
                    document.getElementById('taskId').value = task.id;
                    document.getElementById('title').value = task.title;
                    document.getElementById('description').value = task.description || '';
                    document.getElementById('due_date').value = task.due_date || '';
                    document.getElementById('priority').value = task.priority;
                    document.getElementById('status').value = task.status;
                    document.getElementById('submitBtn').textContent = 'Update Task';
                    document.getElementById('formTitle').textContent = 'Edit Task';
                    document.getElementById('cancelBtn').style.display = 'block';
                    updateSelectColor(document.getElementById('priority'));
                    updateSelectColor(document.getElementById('status'));
                    window.scrollTo(0, 0);
                }

                document.getElementById('cancelBtn').onclick = function() {
                    resetForm();
                }

                function resetForm() {
                    document.getElementById('taskForm').reset();
                    document.getElementById('taskId').value = '';
                    document.getElementById('submitBtn').textContent = 'Create Task';
                    document.getElementById('formTitle').textContent = 'Add New Task';
                    document.getElementById('cancelBtn').style.display = 'none';
                    updateSelectColor(document.getElementById('priority'));
                    updateSelectColor(document.getElementById('status'));
                }

                document.getElementById('taskForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const id = document.getElementById('taskId').value;
                    const title = document.getElementById('title').value;
                    const description = document.getElementById('description').value;
                    const due_date = document.getElementById('due_date').value;
                    const priority = document.getElementById('priority').value;
                    const status = document.getElementById('status').value;

                    const url = id ? `/api/tasks/${id}/` : '/api/tasks/';
                    const method = id ? 'PUT' : 'POST';

                    const response = await fetch(url, {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({title, description, priority, status, due_date})
                    });

                    if(response.ok) {
                        resetForm();
                        loadTasks();
                    } else {
                        const result = await response.json();
                        alert(result.message || 'Error saving task');
                    }
                });

                async function logout() {
                    await fetch('/logout/');
                    window.location.href = '/login/';
                }

                // Initialize colors
                updateSelectColor(document.getElementById('priority'));
                updateSelectColor(document.getElementById('status'));
                loadTasks();
            </script>
        </body>
        </html>
    """)

def validate_task_input(data):
    """Input Validation: Whitelist allowed values and Regex for text fields."""
    errors = []
    if 'priority' in data:
        valid_priorities = [c[0] for c in Task.PRIORITY_CHOICES]
        if data['priority'] not in valid_priorities:
            errors.append(f"Invalid priority. Allowed: {', '.join(valid_priorities)}")
    
    if 'status' in data:
        valid_statuses = [c[0] for c in Task.STATUS_CHOICES]
        if data['status'] not in valid_statuses:
            errors.append(f"Invalid status. Allowed: {', '.join(valid_statuses)}")
            
    # Strict Input Whitelisting: Title (Alphanumeric + basic punctuation)
    if 'title' in data:
        if not re.match(r'^[\w\s\-\.,!?]+$', data['title']):
            errors.append("Invalid title. Only alphanumeric characters and basic punctuation are allowed.")

    # Strict Input Whitelisting: Description (No HTML tags)
    if 'description' in data and data['description']:
        if re.search(r'[<>]', data['description']):
            errors.append("Invalid description. HTML tags are not allowed.")

    # Regex Validation: Due Date (YYYY-MM-DD)
    if 'due_date' in data and data['due_date']:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data['due_date']):
            errors.append("Invalid due date. Format must be YYYY-MM-DD.")
            
    return errors

@require_http_methods(["GET", "POST"])
def task_list_create_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)

    if request.method == 'GET':
        # Return tasks as list of dicts
        tasks = list(Task.objects.filter(user=request.user).values('id', 'title', 'status', 'priority', 'description', 'due_date'))
        return JsonResponse({'status': 'success', 'data': {'tasks': tasks}})

    if request.method == 'POST':
        data = parse_body(request)
        
        # Input Validation
        errors = validate_task_input(data)
        if errors:
            return JsonResponse({'status': 'fail', 'message': 'Validation failed', 'errors': errors}, status=400)

        try:
            # Injection Prevention: Django ORM uses parameterized queries automatically.
            # Mass Assignment Protection: Explicitly selecting fields prevents unauthorized data entry.
            task = Task.objects.create(
                user=request.user,
                title=data.get('title'),
                description=data.get('description', ''),
                priority=data.get('priority', 'Medium'),
                status=data.get('status', 'pending'),
                due_date=data.get('due_date') or None
            )
            return JsonResponse({'status': 'success', 'data': {'task': {
                'id': task.id, 'title': task.title, 'priority': task.priority, 'status': task.status
            }}}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)

@require_http_methods(["DELETE", "PUT"])
def task_detail_view(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)

    try:
        # Granular RBAC: Check specific permissions for global access
        has_global_perm = (
            (request.method == 'DELETE' and request.user.has_perm('task_management.delete_task')) or
            (request.method == 'PUT' and request.user.has_perm('task_management.change_task'))
        )

        if has_global_perm:
            task = Task.objects.get(pk=pk)
        else:
            task = Task.objects.get(pk=pk, user=request.user)
        
        if request.method == 'DELETE':
            task.delete()
            return JsonResponse({'status': 'success'}, status=204)
        
        if request.method == 'PUT':
            data = parse_body(request)
            
            # Input Validation
            errors = validate_task_input(data)
            if errors:
                return JsonResponse({'status': 'fail', 'message': 'Validation failed', 'errors': errors}, status=400)

            # Mass Assignment Protection: Only update fields defined in the whitelist
            for field in FILLABLE_FIELDS:
                if field in data:
                    setattr(task, field, data[field])
            task.save()
            return JsonResponse({'status': 'success', 'data': {'task': {'id': task.id, 'title': task.title}}})

    except Task.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Task not found'}, status=404)