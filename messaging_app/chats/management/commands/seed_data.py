from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils import timezone
from chats.models import User, Conversation, Message

class Command(BaseCommand):
    help = 'Add test users, conversations, and messages without deleting existing data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create 10 users
        users = []
        for _ in range(10):
            username = fake.unique.user_name()
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=fake.unique.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    bio=fake.text(max_nb_chars=100),
                    phone_number=fake.phone_number(),
                    password="password123"
                )
                users.append(user)
        self.stdout.write(self.style.SUCCESS(f"✅ Added {len(users)} new users"))

        # Use existing + new users
        all_users = list(User.objects.all())

        # Create 5 conversations
        conversations = []
        for _ in range(5):
            conv = Conversation.objects.create()
            participants = random.sample(all_users, k=random.randint(2, 4))
            conv.participants.set(participants)
            conversations.append(conv)
        self.stdout.write(self.style.SUCCESS("✅ Added 5 conversations"))

        # Create 100 messages
        messages_created = 0
        for _ in range(100):
            conv = random.choice(conversations)
            sender = random.choice(list(conv.participants.all()))
            Message.objects.create(
                conversation=conv,
                sender=sender,
                message_body=fake.sentence(nb_words=15),
                sent_at=timezone.now()
            )
            messages_created += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Added {messages_created} messages"))

        self.stdout.write(self.style.SUCCESS("🎉 Done seeding without deleting existing data."))
