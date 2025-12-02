from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chatroom


def index(request):
	chatrooms = Chatroom.objects.all()
	return render(request, 'chat/index.html', {'chatrooms': chatrooms})


@login_required
def chatroom(request, room_name):
	room = get_object_or_404(Chatroom, name=room_name)
	return render(request, 'chat/chatroom.html', {
		'room_name': room.name,
		'username': request.user.username
	})
