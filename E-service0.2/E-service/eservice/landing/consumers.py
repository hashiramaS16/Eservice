from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notificaciones_{self.user_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notificacion(self, event):
        await self.send(text_data=json.dumps(event['data']))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.servicio_id = self.scope['url_route']['kwargs']['servicio_id']
        self.group_name = f'chat_{self.servicio_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'data': data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['data'])) 