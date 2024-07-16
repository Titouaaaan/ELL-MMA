import requests

print(requests.get("http://127.0.0.1:8000/").json())

ai_message = 'hello i am the communicator message!'
print(requests.get(f"http://127.0.0.1:8000/sendAIMessage/{ai_message}").json())

human_input = 'Yes I would like to proceed'
print(
    requests.post(
    f"http://127.0.0.1:8000/?input={human_input}"
    ).json()
)