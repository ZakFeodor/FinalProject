import requests
from creds import get_creds

iam_token, folder_id = get_creds()

def ask_gpt(collection):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {'Authorization': f'Bearer {iam_token}', 'Content-Type': 'application/json'}
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": 200},
        "messages": []
    }

    for row in collection:
        content = row['content']
        data["messages"].append({"role": row["role"], "text": content})

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return f"Status code {response.status_code}."
        return response.json()['result']['alternatives'][0]['message']['text']
    except:
        return "Произошла непредвиденная ошибка."