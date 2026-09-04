import os
import sys

# CRITICAL FIX: Add project paths for Vercel
# Get the absolute path of the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Add apps directory to path
apps_dir = os.path.join(project_root, 'apps')
sys.path.insert(0, apps_dir)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_todo.settings')

# Import Django
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except ImportError as e:
    # Fallback if Django isn't found
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

# Vercel requires a variable named "app"
app = application

# Optional: Print for debugging
print(f"✅ wsgi.py loaded from: {project_root}")
