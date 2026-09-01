from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.utils import timezone

def health_check(request):
    """Health check endpoint for Vercel monitoring"""
    status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        connections['default'].cursor()
        status['services']['database'] = 'healthy'
    except OperationalError:
        status['status'] = 'unhealthy'
        status['services']['database'] = 'unhealthy'
    
    return JsonResponse(status)

def vercel_health(request):
    """Vercel-specific health check"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Vercel deployment is running successfully'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('vercel-health/', vercel_health, name='vercel_health'),
    
    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
