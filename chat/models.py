from django.db import models
from django.contrib.auth.models import User


class Chatroom(models.Model):
	name = models.CharField(max_length=100, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class Message(models.Model):
	chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='messages')
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user.username}: {self.content[:50]}"

	class Meta:
		ordering = ['timestamp']
