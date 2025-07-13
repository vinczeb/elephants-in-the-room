from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import os
from .models import Simulation, FavoriteFoodResponse
import random


client = OpenAI(api_key=os.getenv("OPENAI_SECRET"))


class SimulationError(Exception):
    pass


def ask_favorite_food():
    try:
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
                    "content": "Start the conversation by asking what my 3 favorite foods are in a varied but natural "
                               "way."
                }
            ],
            temperature=0.9
        )

        question = response.choices[0].message.content
        print(f"question generated: {question}")
        return question
    except Exception as e:
        print("Failed to generate question about favorite foods")
        raise SimulationError("Failed to generate question about favorite foods") from e


def answer_favorite_food(question):
    personalities = [
        "You are a vegan food blogger from California.",
        "You are a French chef who loves experimenting.",
        "You're a student living in Tokyo who enjoys quick meals.",
        "You're a nostalgic retiree who loves dishes from childhood.",
        "You are a gym-obsessed person who cares more about the results than the taste.",
        "You live in Thailand and enjoy local food.",
        "You are an environmentalist fighting climate change in Australia.",
        "You are a college student in Mumbai who loves spicy street food.",
        "You are a raw vegan who never heats food above 42°C.",
        "You live in your camper van travel around South America.",
        "You follow the carnivore diet.",
        "You live near an ocean and love fishing.",

    ]
    personality = random.choice(personalities)
    print(f"Personality = {personality}")
    system_content = personality + (
        "You're a friendly assistant who answers the question about your top 3 favorite foods. "
        "Give a natural, simple answer listing exactly 3 favorite foods. The answers "
        "should be comma separated in the format food1, food2, food3 and nothing else should be in the answer"
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": question}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
        )

        answer = response.choices[0].message.content.lower()
        print(f"answers generated: {answer}")
        return answer
    except Exception as e:
        print("Failed to generate answers about favorite foods")
        raise SimulationError("Failed to generate answers about favorite foods") from e


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_conversation(request):
    try:
        filter_type = request.GET.get("type", "vegetarian").lower()
        valid_types = {"vegetarian", "vegan"}
        if filter_type not in valid_types:
            return JsonResponse({"error": "Invalid type. Use 'vegetarian' or 'vegan'."}, status=400)
        results = []
        simulation = Simulation.objects.create()
        print(f"Created simulation with id = {simulation.id}")
        for i in range(2):
            print(f"Simulation round {i+1}")
            try:
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
                                   f"is_{filter_type}": is_veg if filter_type == "vegetarian" else is_vegan}
                    results.append(result_item)
            except SimulationError as se:
                print(f"Simulation step {i} skipped due to error: {se}")
                continue
            except Exception as e:
                print(f"Unexpected error during simulation step {i}. {e}")
                continue
        return JsonResponse({f"{filter_type}_responses": results})
    except Exception as e:
        print(f"Unhandled exception in simulating the conversation. {e}")
        return JsonResponse({"error": "Internal server error."}, status=500)


def check_if_vegetarian(foods):
    prompt = (
        "For each of the following foods, determine if the traditional version is vegetarian - "
        "that is, contains no meat, poultry, or fish. "
        "Only consider the traditional or commonly known version of the food as served in most places, "
        "However, if a food is traditionally not vegetarian but it explicitly includes terms like 'vegetarian', "
        "'veggie', or similar, assume it is vegetarian.\n\n"
        f"{', '.join(foods)}\n\n"
        "Are all of these foods vegetarian?\n"
        "Answer only 'Yes' if all items can be made vegetarian in some form. Answer 'No' otherwise."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        print( f"{', '.join(foods)} are vegetarian: {answer}")
        return True if answer == "yes" else False
    except Exception as e:
        print(f"Failed to tell if {', '.join(foods)} are vegetarian")
        raise SimulationError(f"Failed to tell if {', '.join(foods)} are vegetarian") from e


def check_if_vegan(foods):
    prompt = (
        "For each of the following foods, determine if the traditional version is fully vegan — "
        "meaning it contains no animal products such as meat, fish, dairy, eggs, honey, or gelatin. "
        "Assume the food is being served in the way it is typically known or commonly prepared in restaurants or homes. "
        "If the food name includes 'vegan', assume it is vegan. "
        "Do not assume modifications or substitutions unless the food name says 'vegan'.\n\n"
        f"{', '.join(foods)}\n\n"
        "Are all of these foods vegan?\n"
        "Answer only 'Yes' if all items are traditionally vegan or include 'vegan' in the name. Answer 'No' otherwise."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        print( f"{', '.join(foods)} are vegan: {answer}")
        return True if answer == "yes" else False
    except Exception as e:
        print(f"Failed to tell if {', '.join(foods)} are vegan")
        raise SimulationError(f"Failed to tell if {', '.join(foods)} are vegan") from e
