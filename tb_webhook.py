import os
import logging
from aiogram import Bot, Dispatcher, types
import handlers
import json
import os
from database import pool, execute_select_query
from database2 import get_quiz_data

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
# API_TOKEN = '6353924149:AAELVCpnt0U4P_6lW76dm8EaCrqy91--OSQ'


API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(handlers.router)

# функция загружает киз из бд. Он весь хранится в формате JSON в одной ячейке
async def get_quiz_qustions():
    get_questions = f"""
        SELECT question
        FROM `quiz_questions`
        WHERE question_id == 1;
    """   
    results = execute_select_query(pool, get_questions)
    return results[0]["question"]

async def process_event(event):

    update = types.Update.model_validate(json.loads(event['body']), context={"bot": bot})
    await dp.feed_update(bot, update)

async def webhook(event, context):
    #загружаем квиз. Преобразуем из Json формата в объект 
    # и сохраняем ссылки на него в модулях функцией get_quiz_data
    x = await get_quiz_qustions()
    quiz_data = json.loads(x)
    get_quiz_data(quiz_data)
    print (quiz_data)
    if event['httpMethod'] == 'POST':
        # Bot and dispatcher initialization
        # Объект бота
        await process_event(event)
        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}
