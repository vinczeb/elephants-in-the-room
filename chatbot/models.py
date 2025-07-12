from django.db import models
import uuid

class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} at {self.created_at}"


class UserResponse(models.Model):
    id = models.AutoField(primary_key=True)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='response')
    food_1 = models.CharField(max_length=100)
    food_2 = models.CharField(max_length=100)
    food_3 = models.CharField(max_length=100)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)

    def __str__(self):
        return f"Response for {self.conversation.id}"