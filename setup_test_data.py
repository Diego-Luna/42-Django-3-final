#!/usr/bin/env python
"""
Script to create initial test data for EX00 and EX01
Creates users and chat rooms for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'd09.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import Chatroom


def create_test_users():
	"""Create test users for authentication testing"""
	users_data = [
		{'username': 'admin', 'email': 'admin@test.com', 'password': 'admin123', 'is_superuser': True},
		{'username': 'user_1', 'email': 'user1@test.com', 'password': 'password123', 'is_superuser': False},
		{'username': 'user_2', 'email': 'user2@test.com', 'password': 'password123', 'is_superuser': False},
		{'username': 'user_3', 'email': 'user3@test.com', 'password': 'password123', 'is_superuser': False},
	]
	
	for user_data in users_data:
		username = user_data['username']
		if not User.objects.filter(username=username).exists():
			if user_data['is_superuser']:
				User.objects.create_superuser(
					username=username,
					email=user_data['email'],
					password=user_data['password']
				)
				print(f"✓ Superuser created: {username}")
			else:
				User.objects.create_user(
					username=username,
					email=user_data['email'],
					password=user_data['password']
				)
				print(f"✓ User created: {username}")
		else:
			print(f"- User already exists: {username}")


def create_chat_rooms():
	"""Create chat rooms for EX01 testing"""
	rooms = ['General', 'Sports', 'Technology']
	
	for room_name in rooms:
		room, created = Chatroom.objects.get_or_create(name=room_name)
		if created:
			print(f"✓ Chat room created: {room_name}")
		else:
			print(f"- Chat room already exists: {room_name}")


def main():
	print("=" * 50)
	print("Creating test data for EX00 and EX01")
	print("=" * 50)
	print()
	
	print("Creating test users...")
	create_test_users()
	print()
	
	print("Creating chat rooms...")
	create_chat_rooms()
	print()
	
	print("=" * 50)
	print("Test data setup complete!")
	print("=" * 50)
	print()
	print("Test Users:")
	print("  - admin  / admin123 (superuser)")
	print("  - user_1 / password123")
	print("  - user_2 / password123")
	print("  - user_3 / password123")
	print()
	print("Chat Rooms:")
	print("  - General")
	print("  - Sports")
	print("  - Technology")
	print()


if __name__ == '__main__':
	main()
