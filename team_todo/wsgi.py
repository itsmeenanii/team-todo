import os
import sys
import traceback

# CRITICAL: Add project paths for Vercel
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'apps'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_todo.settings')

# Try to import Django
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
    print("✅ Django loaded successfully!")
except Exception as e:
    print(f"❌ Error loading Django: {e}")
    print(traceback.format_exc())
    # Fallback: try importing directly
    import django
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
