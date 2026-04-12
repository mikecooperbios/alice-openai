# Alice-OpenAI Bridge

Сервер-прослойка между навыком Яндекс Алисы и OpenAI API.

## Быстрый старт

1. pip install -r requirements.txt
2. Скопируй .env.example в .env и заполни OPENAI_API_KEY
3. uvicorn main:app --port 8000 --reload
4. Для публичного URL: ngrok http 8000
5. URL навыка в Яндекс Диалогах: https://<ngrok-url>/alice

## Эндпоинты

- GET /health - проверка сервера
- POST /alice - вебхук для Яндекс Алисы

## Модель

gpt-4o-mini (можно заменить на gpt-4o в main.py)
