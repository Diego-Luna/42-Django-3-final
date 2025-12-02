from django.contrib import admin
from .models import Chatroom


@admin.register(Chatroom)
class ChatroomAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_at')
	search_fields = ('name',)
