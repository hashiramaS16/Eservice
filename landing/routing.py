from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notificaciones/(?P<user_id>\d+)/$', consumers.NotificacionConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<servicio_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
] 