import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Add apps directory
apps_dir = os.path.join(project_root, 'apps')
sys.path.insert(0, apps_dir)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_todo.settings')

application = get_wsgi_application()
app = application  # CRITICAL for Vercel
