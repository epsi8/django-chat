from django.contrib import admin
from .models import Conversation, Message, Profile
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display=('id','created_at'); filter_horizontal=('users',)
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=('id','conversation','sender','created_at'); search_fields=('text',)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','last_seen')
