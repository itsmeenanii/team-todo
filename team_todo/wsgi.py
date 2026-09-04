import os
import sys

# Add the project root to the Python path so Vercel can find your modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_todo.settings')

# This is the standard Django WSGI application
application = get_wsgi_application()

# This is the variable Vercel requires and is looking for.
# It must be named exactly "app".
app = application
