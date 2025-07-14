from django.urls import path
from . import views

urlpatterns = [
    path("simulate_conversation/", views.simulate_conversation),
    path('idle/', views.idle_for_three_minutes),

]