from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import os
from .models import Simulation, FavoriteFoodResponse
import random


client = OpenAI(api_key=os.getenv("OPENAI_SECRET"))


def ask_favorite_food():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You're a helpful assistant. "
                    "Your job is to start the conversation by asking the user what their 3 favorite foods are. "
                    "Don't include any greetings or filler like 'Hi', 'Hey there', or 'Sure thing'.  "
                )
            },
            {
                "role": "user",
                "content": "Start the conversation by asking what my 3 favorite foods are in a varied but natural way."
            }
        ],
        temperature=0.9
    )

    question = response.choices[0].message.content
    print(question)
    return question


def answer_favorite_food(question):
    personalities = [
        "You are a vegan food blogger from California.",
        "You are a French chef who loves experimenting.",
        "You're a student living in Tokyo who enjoys quick meals.",
        "You're a nostalgic retiree who loves dishes from childhood.",
        "You are a gym-obsessed person who cares more about the results than the taste.",
        "You live in Thailand and enjoy local food.",
        "You are an environmentalist fighting climate change in Australia.",
        "You are a college student in Mumbai who loves spicy street food."
        "You are a raw vegan who never heats food above 42°C."
        "You live in your camper van travel around South America."
        "You follow the carnivore diet."
        "You live near an ocean and love fishing."

    ]

    system_content = random.choice(personalities) + (
        "You're a friendly assistant who answers the question about your top 3 favorite foods. "
        "Give a natural, simple answer listing exactly 3 favorite foods. The answers "
        "should be comma separated in the format food1, food2, food3 and nothing else should be in the answer"
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
    )

    answer = response.choices[0].message.content.lower()
    print(answer)
    return answer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_conversation(request):
    filter_type = request.GET.get("type", "vegetarian").lower()
    valid_types = {"vegetarian", "vegan"}
    if filter_type not in valid_types:
        return JsonResponse({"error": "Invalid type. Use 'vegetarian' or 'vegan'."}, status=400)
    results = []
    simulation = Simulation.objects.create()
    for _ in range(10):
        question = ask_favorite_food()
        answer = answer_favorite_food(question)
        food_items = [part.strip() for part in answer.split(',')]

        is_veg = check_if_vegetarian(food_items)
        is_vegan = check_if_vegan(food_items)

        FavoriteFoodResponse.objects.create(
            simulation=simulation,
            food_1=food_items[0],
            food_2=food_items[1],
            food_3=food_items[2],
            is_vegetarian=is_veg,
            is_vegan=is_vegan
        )

        if (filter_type == "vegetarian" and is_veg) or (filter_type == "vegan" and is_vegan):
            result_item = {"question": question,
                           "answer": answer,
                           "foods": food_items,
                           f"is_{filter_type}": is_veg if filter_type == "vegetarian" else is_vegan}
            results.append(result_item)
    return JsonResponse({f"{filter_type}_responses": results})


def check_if_vegetarian(foods):
    prompt = (
        "For each of the following foods, consider whether they can be prepared in a vegetarian way - "
        "that is, without any meat, poultry, or fish. Only consider whether a vegetarian version is possible, "
        "even if the default version usually includes meat. For example, sushi or pizza can be vegetarian."
        "However, if the food name explicitly mentions a type of meat, fish, or poultry "
        "(e.g., 'meatloaf', 'chicken wings', 'tuna salad'), it should be considered non-vegetarian, "
        "regardless of possible substitutes..\n\n"
        f"{', '.join(foods)}\n\n"
        "Can all of these foods be made vegetarian?\n"
        "Answer only 'Yes' if all items can be made vegetarian in some form. Answer 'No' otherwise."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    print( f"{', '.join(foods)} are vegetarian: {answer}")
    return True if answer == "yes" else False


def check_if_vegan(foods):
    prompt = (
        "For each of the following foods, consider whether they can be prepared in a fully vegan way - "
        "that is, without any animal products like meat, fish, eggs, or dairy. "
        "Only consider whether a vegan version is possible, "
        "even if the typical version is not vegan. For example, pizza or chocolate cake can be made vegan."
        "If the food explicitly names a type of animal-derived ingredient, it is not vegan.\n\n"
        f"{', '.join(foods)}\n\n"
        "Can all of these foods be made vegan?\n"
        "Answer only 'Yes' if all items can be made vegan in some form. Answer 'No' otherwise."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    print( f"{', '.join(foods)} are vegan: {answer}")
    return True if answer == "yes" else False
