from django.db import models


class Simulation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulation {self.id} at {self.created_at}"


class FavoriteFoodResponse(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='responses')
    food_1 = models.CharField(max_length=100)
    food_2 = models.CharField(max_length=100)
    food_3 = models.CharField(max_length=100)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)

    def __str__(self):
        return f"FavoriteFoodResponse for Conversation {self.simulation.id}"