import requests

url = "http://127.0.0.1:8005/generate"
data = {
    "text": "有哪些年龄小于24岁的人"
}

response = requests.post(url, json=data)
print(response.json()['generated_text'])
