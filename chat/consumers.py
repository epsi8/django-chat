import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])

        allowed = await self.user_in_conversation(
            self.scope["user"].id, self.conversation_id
        )
        if not allowed:
            await self.close()
            return

        self.group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
            text = (data.get("text") or "").strip()
            if not text:
                return

            msg = await self.create_message(
                self.scope["user"].id,
                self.conversation_id,
                text
            )

            payload = {
                "type": "chat.message",
                "id": msg["id"],
                "sender": msg["sender"],
                "text": msg["text"],
                "timestamp": msg["timestamp"],
            }

            await self.channel_layer.group_send(
                self.group_name,
                {"type": "broadcast", "payload": payload}
            )
        except Exception as e:
            import traceback
            traceback.print_exc()

    async def broadcast(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    # --- DB Helpers ---
    @database_sync_to_async
    def user_in_conversation(self, user_id, conv_id):
        return Conversation.objects.filter(id=conv_id, users__id=user_id).exists()

    @database_sync_to_async
    def create_message(self, user_id, conv_id, text):
        try:
            m = Message.objects.create(
                conversation_id=conv_id,  # assumes FK is "conversation"
                sender_id=user_id,        # assumes FK is "sender"
                text=text
            )
            return {
                "id": m.id,
                "sender": m.sender.username,
                "text": m.text,
                "timestamp": timezone.localtime(m.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "id": None,
                "sender": "error",
                "text": str(e),
                "timestamp": "",
            }
