from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Channel, ChannelMembership, Message, DirectMessage, MessageReaction
from .serializers import (
    ChannelSerializer, ChannelCreateSerializer, ChannelMembershipSerializer,
    MessageSerializer, MessageCreateSerializer, DirectMessageSerializer,
    DirectMessageCreateSerializer, MessageReactionSerializer, MessageReactionCreateSerializer
)


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for Channel model"""
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChannelCreateSerializer
        return ChannelSerializer
    
    @action(detail=False, methods=['get'])
    def my_channels(self, request):
        """Get channels where current user is a member"""
        memberships = ChannelMembership.objects.filter(user=request.user)
        channels = [membership.channel for membership in memberships]
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a channel"""
        channel = self.get_object()
        
        # Check if user is already a member
        if ChannelMembership.objects.filter(channel=channel, user=request.user).exists():
            return Response(
                {'error': 'Already a member of this channel'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = ChannelMembership.objects.create(
            channel=channel,
            user=request.user
        )
        
        serializer = ChannelMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a channel"""
        channel = self.get_object()
        
        try:
            membership = ChannelMembership.objects.get(
                channel=channel, user=request.user
            )
            membership.delete()
            return Response({'message': 'Successfully left channel'})
        except ChannelMembership.DoesNotExist:
            return Response(
                {'error': 'Not a member of this channel'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get channel members"""
        channel = self.get_object()
        memberships = ChannelMembership.objects.filter(channel=channel)
        serializer = ChannelMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """Filter messages based on user's channel memberships"""
        user_channels = ChannelMembership.objects.filter(user=self.request.user).values_list('channel_id', flat=True)
        return self.queryset.filter(channel_id__in=user_channels)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message"""
        message = self.get_object()
        reaction_type = request.data.get('reaction_type')
        
        if not reaction_type:
            return Response(
                {'error': 'reaction_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already reacted with this type
        existing_reaction = MessageReaction.objects.filter(
            message=message, user=request.user, reaction_type=reaction_type
        ).first()
        
        if existing_reaction:
            # Remove existing reaction
            existing_reaction.delete()
            return Response({'message': 'Reaction removed'})
        else:
            # Create new reaction
            reaction = MessageReaction.objects.create(
                message=message,
                user=request.user,
                reaction_type=reaction_type
            )
            serializer = MessageReactionSerializer(reaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_channel(self, request):
        """Get messages for a specific channel"""
        channel_id = request.query_params.get('channel_id')
        if not channel_id:
            return Response(
                {'error': 'channel_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is a member of the channel
        if not ChannelMembership.objects.filter(
            channel_id=channel_id, user=request.user
        ).exists():
            return Response(
                {'error': 'Not a member of this channel'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = self.get_queryset().filter(channel_id=channel_id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class DirectMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for DirectMessage model"""
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DirectMessageCreateSerializer
        return DirectMessageSerializer
    
    def get_queryset(self):
        """Filter messages to show only those involving current user"""
        return self.queryset.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        )
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with a specific user"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            Q(sender_id=other_user_id, recipient=request.user) |
            Q(sender=request.user, recipient_id=other_user_id)
        ).order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a direct message as read"""
        message = self.get_object()
        
        # Only recipient can mark as read
        if message.recipient != request.user:
            return Response(
                {'error': 'Only recipient can mark message as read'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_read = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages"""
        unread_count = self.get_queryset().filter(
            recipient=request.user, is_read=False
        ).count()
        
        return Response({'unread_count': unread_count})


class MessageReactionViewSet(viewsets.ModelViewSet):
    """ViewSet for MessageReaction model"""
    queryset = MessageReaction.objects.all()
    serializer_class = MessageReactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageReactionCreateSerializer
        return MessageReactionSerializer
    
    def get_queryset(self):
        """Filter reactions to messages in user's channels"""
        user_channels = ChannelMembership.objects.filter(user=self.request.user).values_list('channel_id', flat=True)
        return self.queryset.filter(message__channel_id__in=user_channels)
