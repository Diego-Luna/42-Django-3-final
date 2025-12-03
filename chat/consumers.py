import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chatroom, Message


class ChatConsumer(AsyncWebsocketConsumer):
	# * Class-level dictionary to track connected users per room
	connected_users = {}
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

		# ! Add user to connected users list for this room
		if self.room_group_name not in ChatConsumer.connected_users:
			ChatConsumer.connected_users[self.room_group_name] = set()
		ChatConsumer.connected_users[self.room_group_name].add(self.user.username)

		# * Send last 3 messages as history
		history = await self.get_message_history()
		if history:
			await self.send(text_data=json.dumps({
				'type': 'history',
				'messages': history
			}))

		# ! Send current user list to the newly connected user
		await self.send(text_data=json.dumps({
			'type': 'user_list',
			'users': list(ChatConsumer.connected_users[self.room_group_name])
		}))

		# ! Notify all users in the room that a new user joined
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'user_join',
				'username': self.user.username,
				'users': list(ChatConsumer.connected_users[self.room_group_name])
			}
		)

	async def disconnect(self, close_code):
		if hasattr(self, 'room_group_name') and hasattr(self, 'user'):
			# * Remove user from connected users list
			if self.room_group_name in ChatConsumer.connected_users:
				ChatConsumer.connected_users[self.room_group_name].discard(self.user.username)
				
				# ! Notify all users that this user left
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'user_leave',
						'username': self.user.username,
						'users': list(ChatConsumer.connected_users[self.room_group_name])
					}
				)
				
				# ! Clean up empty room
				if not ChatConsumer.connected_users[self.room_group_name]:
					del ChatConsumer.connected_users[self.room_group_name]
			
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
			'username': event['username'],
			'users': event['users']
		}))

	async def user_leave(self, event):
		await self.send(text_data=json.dumps({
			'type': 'user_leave',
			'username': event['username'],
			'users': event['users']
		}))

	async def user_list(self, event):
		await self.send(text_data=json.dumps({
			'type': 'user_list',
			'users': event['users']
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
