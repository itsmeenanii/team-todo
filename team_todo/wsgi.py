"""
WSGI config for collaborative_todo project.
It exposes the WSGI callable as a module-level variable named ``application``.
Vercel requires a variable named ``app``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_todo.settings')

# Standard Django application
application = get_wsgi_application()

# Vercel requires a variable named "app"
app = application
