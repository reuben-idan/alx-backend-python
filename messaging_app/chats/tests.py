"""
Comprehensive unit tests for the messaging app views.
Tests cover all CRUD operations, permissions, edge cases, and error handling.
"""

import uuid
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from chats.models import User, Conversation, Message
from chats.serializers import UserSerializer, ConversationSerializer, MessageSerializer


class UserViewTestCase(APITestCase):
    """Test cases for UserView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio',
            'phone_number': '+1234567890',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        }
        
        # Create a test user for authentication tests
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            phone_number='+0987654321',
            password='ExistingPassword123!'
        )
        
        # Create another user for permission tests
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            first_name='Other',
            last_name='User',
            phone_number='+1122334455',
            password='OtherPassword123!'
        )

    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_create_user_success(self):
        """Test successful user creation"""
        url = reverse('users-list')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_create_user_missing_password(self):
        """Test user creation fails without password"""
        url = reverse('users-list')
        data = self.user_data.copy()
        del data['password']
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Password and confirm_password are required', str(response.data))

    def test_create_user_missing_confirm_password(self):
        """Test user creation fails without confirm_password"""
        url = reverse('users-list')
        data = self.user_data.copy()
        del data['confirm_password']
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_mismatch(self):
        """Test user creation fails when passwords don't match"""
        url = reverse('users-list')
        data = self.user_data.copy()
        data['confirm_password'] = 'DifferentPassword123!'
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords do not match', str(response.data))

    def test_create_user_weak_password(self):
        """Test user creation fails with weak password"""
        url = reverse('users-list')
        data = self.user_data.copy()
        data['password'] = data['confirm_password'] = '123'
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_username(self):
        """Test user creation fails with duplicate username"""
        url = reverse('users-list')
        data = self.user_data.copy()
        data['username'] = self.existing_user.username
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_email(self):
        """Test user creation fails with duplicate email"""
        url = reverse('users-list')
        data = self.user_data.copy()
        data['email'] = self.existing_user.email
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_while_authenticated_fails(self):
        """Test that authenticated users cannot create new accounts"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-list')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Logged in users cannot create new account', str(response.data))

    def test_get_user_list_requires_authentication(self):
        """Test that getting user list requires authentication"""
        url = reverse('users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_list_authenticated(self):
        """Test getting user list when authenticated"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_user_detail_requires_authentication(self):
        """Test that getting user detail requires authentication"""
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_authenticated(self):
        """Test getting user detail when authenticated"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.existing_user.username)

    def test_update_own_user_profile(self):
        """Test that users can update their own profile"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        data = {'bio': 'Updated bio'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')

    def test_update_other_user_profile_fails(self):
        """Test that users cannot update other users' profiles"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.other_user.user_id})
        data = {'bio': 'Hacked bio'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_password_success(self):
        """Test successful password update"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        data = {
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_partial_update_without_password_fields(self):
        """Test that user can update profile without providing password fields"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        data = {'bio': 'Updated bio without password'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio without password')
    
    def test_update_username_to_existing_one_fails(self):
        """Test that updating username to an existing one fails"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        data = {'username': self.other_user.username}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_password_mismatch(self):
        """Test password update fails when passwords don't match"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        data = {
            'password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_own_user_account(self):
        """Test that users can delete their own account"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.existing_user.user_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(user_id=self.existing_user.user_id).exists())

    def test_delete_other_user_account_fails(self):
        """Test that users cannot delete other users' accounts"""
        tokens = self.get_tokens_for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('users-detail', kwargs={'pk': self.other_user.user_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ConversationViewTestCase(APITestCase):
    """Test cases for ConversationView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            phone_number='+1111111111',
            password='Password123!'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            phone_number='+2222222222',
            password='Password123!'
        )
        
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            first_name='User',
            last_name='Three',
            phone_number='+3333333333',
            password='Password123!'
        )
        
        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_create_conversation_success(self):
        """Test successful conversation creation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-list')
        data = {'participants': ['user2']}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('conversation_id', response.data)
        
        # Check that the creator is automatically added as participant
        conversation = Conversation.objects.get(conversation_id=response.data['conversation_id'])
        self.assertIn(self.user1, conversation.participants.all())

    def test_create_conversation_requires_authentication(self):
        """Test that creating conversation requires authentication"""
        url = reverse('conversations-list')
        data = {'participants': ['user2']}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_conversation_with_empty_participants(self):
        """Test that conversation is created with only creator when empty participants list is provided"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-list')
        data = {'participants': []}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation = Conversation.objects.get(conversation_id=response.data['conversation_id'])
        self.assertEqual(conversation.participants.count(), 1)
        self.assertIn(self.user1, conversation.participants.all())
    
    def test_create_conversation_with_nonexistent_participant_fails(self):
        """Test that conversation creation fails with non-existent participant"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-list')
        data = {'participants': ['nonexistent_user']}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_conversations_requires_authentication(self):
        """Test that getting conversations requires authentication"""
        url = reverse('conversations-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_conversations_only_shows_user_conversations(self):
        """Test that users only see conversations they participate in"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Create another conversation without user1
        other_conversation = Conversation.objects.create()
        other_conversation.participants.add(self.user2, self.user3)
        
        url = reverse('conversations-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the conversation with user1
        self.assertEqual(response.data[0]['conversation_id'], str(self.conversation.conversation_id))

    def test_get_conversation_detail_participant_only(self):
        """Test that only participants can view conversation details"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': self.conversation.conversation_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['conversation_id'], str(self.conversation.conversation_id))

    def test_get_conversation_detail_non_participant_fails(self):
        """Test that non-participants cannot view conversation details"""
        tokens = self.get_tokens_for_user(self.user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': self.conversation.conversation_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_conversation_participant_only(self):
        """Test that only participants can update conversations"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': self.conversation.conversation_id})
        data = {'participants': ['user1', 'user2', 'user3']}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_conversation_non_participant_fails(self):
        """Test that non-participants cannot update conversations"""
        tokens = self.get_tokens_for_user(self.user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': self.conversation.conversation_id})
        data = {'participants': ['user1', 'user2', 'user3']}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_conversation_participant_only(self):
        """Test that only participants can delete conversations"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': self.conversation.conversation_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Conversation.objects.filter(conversation_id=self.conversation.conversation_id).exists())

    def test_add_participant_success(self):
        """Test successfully adding a participant to conversation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-add-participant', kwargs={'pk': self.conversation.conversation_id})
        data = {'user_id': str(self.user3.user_id)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('added to conversation', response.data['success'])
        self.assertIn(self.user3, self.conversation.participants.all())

    def test_add_participant_non_member_fails(self):
        """Test that non-members cannot add participants"""
        tokens = self.get_tokens_for_user(self.user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-add-participant', kwargs={'pk': self.conversation.conversation_id})
        data = {'user_id': str(self.user1.user_id)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_participant_missing_user_id(self):
        """Test adding participant fails without user_id"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-add-participant', kwargs={'pk': self.conversation.conversation_id})
        data = {}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User ID is required', response.data['error'])

    def test_add_participant_invalid_user_id(self):
        """Test adding participant fails with invalid user_id"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-add-participant', kwargs={'pk': self.conversation.conversation_id})
        data = {'user_id': str(uuid.uuid4())}  # Non-existent user ID
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_existing_participant(self):
        """Test adding a participant who is already in the conversation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-add-participant', kwargs={'pk': self.conversation.conversation_id})
        data = {'user_id': str(self.user2.user_id)}  # user2 is already a participant
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already exists in conversation', response.data['message'])
    
    def test_conversation_with_many_participants(self):
        """Test conversation with many participants works correctly"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Create many users
        participants = []
        for i in range(4, 15):  # Create 10 additional users
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                first_name=f'User{i}',
                last_name='Test',
                phone_number=f'+1234567{i}',
                password='Password123!'
            )
            participants.append(user.username)
        
        url = reverse('conversations-list')
        data = {'participants': participants}
        response = self.client.post(url, data, format='json')
        
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation = Conversation.objects.get(conversation_id=response.data['conversation_id'])
        self.assertEqual(conversation.participants.count(), len(participants) + 1)  # +1 for creator
    
    def test_invalid_uuid_format_fails(self):
        """Test that invalid UUID format returns 404"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversations-detail', kwargs={'pk': 'invalid-uuid'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MessageViewTestCase(APITestCase):
    """Test cases for MessageView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            phone_number='+1111111111',
            password='Password123!'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            phone_number='+2222222222',
            password='Password123!'
        )
        
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            first_name='User',
            last_name='Three',
            phone_number='+3333333333',
            password='Password123!'
        )
        
        # Create conversations
        self.conversation1 = Conversation.objects.create()
        self.conversation1.participants.add(self.user1, self.user2)
        
        self.conversation2 = Conversation.objects.create()
        self.conversation2.participants.add(self.user2, self.user3)
        
        # Create messages
        self.message1 = Message.objects.create(
            conversation=self.conversation1,
            sender=self.user1,
            message_body="Hello from user1"
        )
        
        self.message2 = Message.objects.create(
            conversation=self.conversation1,
            sender=self.user2,
            message_body="Hello from user2"
        )

    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_create_message_success(self):
        """Test successful message creation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        data = {'message_body': 'New test message'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_body'], 'New test message')
        self.assertEqual(response.data['username'], self.user1.username)

    def test_create_message_requires_authentication(self):
        """Test that creating message requires authentication"""
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        data = {'message_body': 'Unauthorized message'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_message_invalid_conversation(self):
        """Test creating message in non-existent conversation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        fake_conversation_id = uuid.uuid4()
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': fake_conversation_id})
        data = {'message_body': 'Message to nowhere'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_messages_success(self):
        """Test getting messages from a conversation"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two messages in conversation1

    def test_get_messages_only_from_specific_conversation(self):
        """Test that messages are filtered by conversation"""
        # Create a message in conversation2
        Message.objects.create(
            conversation=self.conversation2,
            sender=self.user2,
            message_body="Message in conversation2"
        )
        
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Still only messages from conversation1

    def test_get_message_detail_success(self):
        """Test getting a specific message"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message1.message_id
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message_body'], self.message1.message_body)

    def test_update_own_message_success(self):
        """Test successfully updating own message"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message1.message_id
        })
        data = {'message_body': 'Updated message'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message_body'], 'Updated message')

    def test_update_other_user_message_fails(self):
        """Test that users cannot update messages from other users"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message2.message_id  # message2 is from user2
        })
        data = {'message_body': 'Hacked message'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', str(response.data))

    def test_delete_own_message_success(self):
        """Test successfully deleting own message"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message1.message_id
        })
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(message_id=self.message1.message_id).exists())

    def test_delete_other_user_message_fails(self):
        """Test that users cannot delete messages from other users"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message2.message_id  # message2 is from user2
        })
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have permission to perform this action.', str(response.data))

    def test_message_create_empty_body_fails(self):
        """Test that creating message with empty body fails"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        data = {'message_body': ''}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_message_includes_sender_info(self):
        """Test that message response includes sender information"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message1.message_id
        })
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['first_name'], self.user1.first_name)
        self.assertEqual(response.data['last_name'], self.user1.last_name)
    
    def test_messages_are_ordered_by_sent_at(self):
        """Test that messages are returned in chronological order"""
        # Create a third message with earlier timestamp
        earlier_message = Message.objects.create(
            conversation=self.conversation1,
            sender=self.user1,
            message_body="Earlier message",
        )
        earlier_message.sent_at = self.message1.sent_at - timedelta(minutes=5)
        earlier_message.save()
        
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the order is correct (earlier message first)
        self.assertEqual(response.data[0]['message_id'], str(earlier_message.message_id))
        self.assertEqual(response.data[1]['message_id'], str(self.message1.message_id))
        self.assertEqual(response.data[2]['message_id'], str(self.message2.message_id))

    def test_create_message_with_empty_body_fails(self):
        """Test that creating message with empty body fails"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': self.conversation1.conversation_id})
        data = {'message_body': ''}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_read_only_fields_cannot_be_updated(self):
        """Test that read-only fields cannot be updated"""
        tokens = self.get_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': self.conversation1.conversation_id,
            'pk': self.message1.message_id
        })
        original_sent_at = self.message1.sent_at
        data = {
            'message_body': 'Updated message',
            'sent_at': '2020-01-01T00:00:00Z',  # Try to modify read-only field
            'sender': str(self.user2.user_id)    # Try to modify read-only field
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify read-only fields weren't changed
        updated_message = Message.objects.get(message_id=self.message1.message_id)
        self.assertEqual(updated_message.sent_at, original_sent_at)
        self.assertEqual(updated_message.sender, self.user1)


