import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tareas_project.settings')

# Initialize Django ASGI app first so AppRegistry is populated
# before importing own consumers that reference models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from core.consumers import NotificationConsumer

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/notifications/', NotificationConsumer.as_asgi()),
        ])
    ),
})
