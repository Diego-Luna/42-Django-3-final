import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chatroom, Message


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

		# * Send last 3 messages as history
		history = await self.get_message_history()
		if history:
			await self.send(text_data=json.dumps({
				'type': 'history',
				'messages': history
			}))

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
			# * Save message to database
			await self.save_message(message)

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

	@database_sync_to_async
	def save_message(self, content):
		chatroom = Chatroom.objects.get(name=self.room_name)
		Message.objects.create(
			chatroom=chatroom,
			user=self.user,
			content=content
		)

	@database_sync_to_async
	def get_message_history(self):
		try:
			chatroom = Chatroom.objects.get(name=self.room_name)
			messages = Message.objects.filter(chatroom=chatroom).order_by('-timestamp')[:3]
			# ! Convert to list and reverse to show oldest to newest
			messages_list = list(messages)
			messages_list.reverse()
			return [
				{
					'username': msg.user.username,
					'message': msg.content,
					'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
				}
				for msg in messages_list
			]
		except Chatroom.DoesNotExist:
			return []
