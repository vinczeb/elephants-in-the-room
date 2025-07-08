from django.urls import path
from . import views

urlpatterns = [
    path("", views.ask_favorite_food, name="chat"),
]