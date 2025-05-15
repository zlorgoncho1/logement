# Logement Project

A Django-based web application for managing housing/logement.

**This is a Guided Project made with DIT Students, incorporating Vibe Coding tips and techniques.**

## Project Structure

```
logement/
├── logement/                  # Main project directory
│   ├── __init__.py
│   ├── settings.py           # Project settings and configuration
│   ├── urls.py              # URL routing configuration
│   ├── views.py             # View definitions
│   ├── wsgi.py              # WSGI application entry point
│   ├── asgi.py              # ASGI application entry point
│   └── __pycache__/         # Python cache directory
├── accounts/                 # User authentication and management app
├── bookings/                # Booking management app
├── core/                    # Core functionality app
├── messaging/              # Messaging system app
├── payment/                # Payment processing app
├── properties/             # Property listing and management app
├── reviews/                # User reviews and ratings app
├── .cursor/                # Cursor IDE specific directory
│   └── rules/             # Contains Cursor IDE specific rules
├── docs/                   # Project documentation
├── env/                    # Virtual environment directory
├── fichiers/              # File storage directory
├── media/                 # User-uploaded media files
├── static/                # Static files (CSS, JS, images)
├── staticfiles/           # Collected static files
├── templates/             # HTML templates
├── .env                   # Environment variables
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore rules
├── db.sqlite3            # SQLite database
├── manage.py             # Django's command-line utility
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Development Environment

This project uses Cursor IDE for development. The `.cursor` directory contains IDE-specific configurations and rules that help maintain code quality and consistency.

### Cursor IDE Integration

The `.cursor` directory is automatically managed by the Cursor IDE and contains:
- Custom rules and configurations for the project
- IDE-specific settings
- Code formatting and linting rules

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd logement
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Unix/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   # Upgrade pip first
   python -m pip install --upgrade pip

   # Install requirements
   pip install -r requirements.txt
   ```

4. Configure the environment:
   ```bash
   # Create a .env file (if needed)
   cp .env.example .env  # If you have an example env file
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser (admin account):
   ```bash
   python manage.py createsuperuser
   ```

### Running the Project

1. Start the development server:
   ```bash
   # Run on default port (8000)
   python manage.py runserver

   # Run on specific port
   python manage.py runserver 8080

   # Run on specific IP and port
   python manage.py runserver 0.0.0.0:8000
   ```

2. Access the application:
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

### Development Commands

```bash
# Run tests
python manage.py test

# Check for code style issues
python manage.py check

# Create new app
python manage.py startapp app_name

# Collect static files
python manage.py collectstatic

# Create new migration
python manage.py makemigrations app_name

# Show migration status
python manage.py showmigrations
```

## Requirements

- Python 3.8+
- Django 4.x
- Other dependencies listed in requirements.txt

## Contributing

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests and ensure they pass
4. Submit a pull request

## License

[Add your license information here] 