from rest_framework import serializers
from .models import Channel, ChannelMembership, Message, DirectMessage, MessageReaction
from core.serializers import UserSerializer, GeographicAreaSerializer


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for Channel model"""
    created_by = UserSerializer(read_only=True)
    area = GeographicAreaSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Channel
        fields = ['id', 'name', 'area', 'created_by', 'is_private', 
                 'created_at', 'updated_at', 'member_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ChannelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new channels"""
    class Meta:
        model = Channel
        fields = ['id', 'name', 'area', 'is_private']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        channel = super().create(validated_data)
        
        # Automatically add creator as admin member
        ChannelMembership.objects.create(
            channel=channel,
            user=validated_data['created_by'],
            is_admin=True
        )
        
        return channel


class ChannelMembershipSerializer(serializers.ModelSerializer):
    """Serializer for ChannelMembership model"""
    user = UserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    
    class Meta:
        model = ChannelMembership
        fields = ['id', 'channel', 'user', 'joined_at', 'is_admin']
        read_only_fields = ['id', 'joined_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    author = UserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'channel', 'author', 'content', 'is_anonymous', 
                 'contains_pii', 'restricted_to_names', 'created_at', 
                 'updated_at', 'reactions']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_reactions(self, obj):
        reactions = {}
        for reaction in obj.reactions.all():
            reaction_type = reaction.reaction_type
            if reaction_type not in reactions:
                reactions[reaction_type] = 0
            reactions[reaction_type] += 1
        return reactions


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    class Meta:
        model = Message
        fields = ['id', 'channel', 'content', 'is_anonymous', 'contains_pii', 'restricted_to_names']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class DirectMessageSerializer(serializers.ModelSerializer):
    """Serializer for DirectMessage model"""
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'recipient', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class DirectMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new direct messages"""
    class Meta:
        model = DirectMessage
        fields = ['recipient', 'content']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for MessageReaction model"""
    user = UserSerializer(read_only=True)
    message = MessageSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'message', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class MessageReactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new message reactions"""
    class Meta:
        model = MessageReaction
        fields = ['message', 'reaction_type']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
