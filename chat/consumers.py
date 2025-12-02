import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = f'chat_{self.room_name}'
		self.user = self.scope['user']

		if not self.user.is_authenticated:
			await self.close()
			return

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		await self.accept()

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'user_join',
				'username': self.user.username
			}
		)

	async def disconnect(self, close_code):
		if hasattr(self, 'room_group_name'):
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)

	async def receive(self, text_data):
		data = json.loads(text_data)
		message = data.get('message', '')

		if message:
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'chat_message',
					'message': message,
					'username': self.user.username
				}
			)

	async def chat_message(self, event):
		await self.send(text_data=json.dumps({
			'type': 'message',
			'message': event['message'],
			'username': event['username']
		}))

	async def user_join(self, event):
		await self.send(text_data=json.dumps({
			'type': 'user_join',
			'username': event['username']
		}))
