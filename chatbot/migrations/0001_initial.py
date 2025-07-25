# Generated by Django 5.2.4 on 2025-07-12 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteFoodResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_1', models.CharField(max_length=100)),
                ('food_2', models.CharField(max_length=100)),
                ('food_3', models.CharField(max_length=100)),
                ('is_vegetarian', models.BooleanField(default=False)),
                ('is_vegan', models.BooleanField(default=False)),
                ('simulation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='chatbot.simulation')),
            ],
        ),
    ]
