from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=timezone.now)

    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(seconds=60)

    def __str__(self):
        return f"Profile({self.user.username})"


# --- Signals to create/save Profile automatically ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Conversation(models.Model):
    users = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        names = ', '.join(sorted(self.users.values_list('username', flat=True)))
        return f"Conversation({names})"

    @staticmethod
    def get_or_create_dm(user1, user2):
        """Return existing or create a new conversation between two users."""
        if user1.id > user2.id:
            user1, user2 = user2, user1
        qs = Conversation.objects.filter(users=user1).filter(users=user2)
        if qs.exists():
            return qs.first(), False
        c = Conversation.objects.create()
        c.users.add(user1, user2)
        return c, True


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.conversation_id}:{self.sender.username}: {self.text[:20]}"
