from django.urls import path
from . import views

urlpatterns = [
    path("simulate_conversation/", views.simulate_conversation),
]