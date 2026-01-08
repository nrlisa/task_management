# Task Management System

## Prerequisites

Before you begin, ensure you have met the following requirements:
*   **Python**: Version 3.8 or higher installed.
*   **Git**: Installed on your machine.

## Installation

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd task-management
    ```

2.  **Create a Virtual Environment**
    It is best practice to run Python projects in a virtual environment to isolate dependencies.

    *   **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

    *   **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a file named `.env` in the root directory of the project. This file is ignored by Git for security reasons. Add the following variables:

```ini
JWT_SECRET=your_super_secret_key_here
# Add other keys if necessary (e.g., DJANGO_SECRET_KEY, DEBUG=True)
```

## Running the Application

1.  **Apply Database Migrations**
    ```bash
    python manage.py migrate
    ```

2.  **Start the Server**
    ```bash
    python manage.py runserver
    ```

    Access the application at `http://127.0.0.1:8000/`.
