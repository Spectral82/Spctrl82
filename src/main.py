import os

import requests
from dotenv import load_dotenv

load_dotenv(".env")

API_KEY = os.getenv("API_KEY")

# Получение значения переменной GITHUB_TOKEN из .env-файла
github_token = os.getenv("GITHUB_TOKEN")

# Создание заголовка с токеном доступа API
headers = {"Authorization": f"token {github_token}"}

# Отправка GET-запроса к API
response = requests.get("https://api.github.com/user", headers=headers)

# Обработка ответа
print(response.json())
