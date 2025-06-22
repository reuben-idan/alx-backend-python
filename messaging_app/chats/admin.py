from django.contrib import admin
from .models import User, Conversation, Message

# Register your models here.
@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    search_fields = ['username', 'email']

admin.site.register(Conversation)
admin.site.register(Message)