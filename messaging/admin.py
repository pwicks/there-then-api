from django.contrib import admin
from .models import Channel, ChannelMembership, Message, DirectMessage, MessageReaction


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'created_by', 'is_private', 'member_count', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['name', 'area__name', 'created_by__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChannelMembership)
class ChannelMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'is_admin', 'joined_at']
    list_filter = ['is_admin', 'joined_at']
    search_fields = ['user__email', 'channel__name']
    ordering = ['-joined_at']
    readonly_fields = ['joined_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'channel', 'content_preview', 'is_anonymous', 'contains_pii', 'created_at']
    list_filter = ['is_anonymous', 'contains_pii', 'created_at']
    search_fields = ['author__email', 'channel__name', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__email', 'recipient__email', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__email', 'message__content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
