from django.db import models
from django.contrib.auth import get_user_model
from core.models import GeographicArea
import uuid

User = get_user_model()


class Channel(models.Model):
    """Messaging channel for a specific location and time period"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    area = models.ForeignKey(GeographicArea, on_delete=models.CASCADE, related_name='channels')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_channels')
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messaging_channel'
        unique_together = ['area', 'name']
    
    def __str__(self):
        return f"{self.name or 'Unnamed Channel'} - {self.area}"
    
    @property
    def member_count(self):
        return self.members.count()


class ChannelMembership(models.Model):
    """User membership in messaging channels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'messaging_channel_membership'
        unique_together = ['channel', 'user']
    
    def __str__(self):
        return f"{self.user.email} in {self.channel}"


class Message(models.Model):
    """Individual messages in channels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_messages')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    contains_pii = models.BooleanField(default=False)
    restricted_to_names = models.JSONField(default=list, blank=True)  # List of names that can see this message
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messaging_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_anonymous']),
        ]
    
    def __str__(self):
        return f"{self.author.email}: {self.content[:50]}..."


class DirectMessage(models.Model):
    """Direct messages between two users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_direct_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_direct_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messaging_direct_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.email} -> {self.recipient.email}: {self.content[:50]}..."


class MessageReaction(models.Model):
    """Reactions to messages (likes, etc.)"""
    REACTION_TYPES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('laugh', 'Laugh'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messaging_message_reaction'
        unique_together = ['message', 'user', 'reaction_type']
    
    def __str__(self):
        return f"{self.user.email} {self.reaction_type} on {self.message.id}"
