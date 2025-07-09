from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import os


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
                    "Don't include any greetings or filler like 'Hi', 'Hey there', or 'Sure thing'. "
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
    system_content = (
        "You're a friendly assistant who answers the question about your top 3 favorite foods. "
        "Give a natural, simple answer listing exactly 3 favorite foods."
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

    answer = response.choices[0].message.content
    print(answer)
    return answer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def simulate_conversation(request):
    question = ask_favorite_food()
    answer = answer_favorite_food(question)
    return JsonResponse({
        "question": question,
        "answer": answer
    })