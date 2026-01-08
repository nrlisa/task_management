Task Management System (Secure Implementation)
📌 Project Overview
This is a secure Task Management Platform built using Django. It implements various security controls based on the OWASP Top 10 and ASVS v4.0.3 standards, specifically focusing on Input Validation, Authentication, and Access Control (RBAC).

🛠 Prerequisites
Before you begin, ensure you have the following installed:

Python: Version 3.8 or higher.

Git: To clone and manage the repository.

🚀 Installation & Setup
1. Clone the Repository
Bash

git clone https://github.com/nrlisa/task_management.git
cd task_management
2. Create and Activate Virtual Environment
You must activate the virtual environment every time you open a new terminal to avoid ImportError.

Windows:

Bash

python -m venv venv
venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate
3. Install Required Packages
Bash

pip install -r requirements.txt
🔐 Configuration (Environment Variables)
For security reasons, the .env file is not included in the repository. You must create one manually in the root folder.

Create a file named .env.

Add the following keys (ask Member 1/2 for the actual secret values via personal message):

Ini, TOML

SECRET_KEY=your_django_secret_key_here
JWT_SECRET=your_jwt_secret_key_here
DEBUG=True
💾 Database & Admin Setup
1. Apply Migrations
This creates the database tables required for the system to function.

Bash

python manage.py makemigrations
python manage.py migrate
2. Create a Superuser (Admin)
To test the Role-Based Access Control (RBAC) and manage users, create an admin account:

Bash

python manage.py createsuperuser
Follow the prompts in the terminal to set your username and password.

💻 Running the Application
Start the Server:

Bash

python manage.py runserver
Access the Platform:

Main App: http://127.0.0.1:8000/

Admin Dashboard: http://127.0.0.1:8000/admin/

🛡 Security Features Implemented
Input Validation: Regex and whitelisting to prevent SQL Injection (A03:2021).

Authentication: Secure session management and password hashing (A07:2021).

Access Control: Middleware implementation to prevent IDOR and unauthorized access (A01:2021).

Output Encoding: Auto-escaping to prevent Cross-Site Scripting (XSS).

📋 Troubleshooting for Collaborators
Button not clicking? Ensure you are running the server via runserver and not just opening the .html file. Check that your .env file is present.

ImportError? Check if (venv) is visible in your terminal. If not, run the activation command in Step 2.

403 Forbidden? This is likely a CSRF or RBAC issue. Ensure you are logged in with the correct permissions.
