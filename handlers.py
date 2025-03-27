from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json
from service import get_stat
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index
from database2 import Asyncrange
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
router = Router()
quiz_data = None

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, mode = False)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

  
@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, mode = False, start = "Not")


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Окончить игру"))
    builder.add(types.KeyboardButton(text="Показать статистику"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на текст окончить игру или команду /stop
@router.message(F.text=="Окончить игру")
@router.message(Command("stop"))
async def cmd_start(message: types.Message):
    await message.answer("Опрос остановлен")
    #Цикл убирающий клавиатуры с сообщений. Работает на 20 сообщений назад.
    async for i in Asyncrange(20):
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.from_user.id,
                message_id=message.message_id-i,
                reply_markup=None
            )
        except TelegramBadRequest:
            pass
        except TelegramRetryAfter:
            pass 

# Хэндлер на текст Начать игру или команду quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    #Картинка хранится в бакете яндекс клауд. Картинка публична. Отправляем картинку по URL.
    await message.bot.send_photo(message.chat.id, photo=f"https://storage.yandexcloud.net/bot-imagebacket/for_bot.jpg")
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
    #Цикл убирающий клавиатуры с сообщений. Работает на 20 сообщений назад.
    async for i in Asyncrange(20):
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.from_user.id,
                message_id=message.message_id-i,
                reply_markup=None
            )
        except TelegramBadRequest:
            pass
        except TelegramRetryAfter:
            pass 
            
@router.message(F.text == "Показать статистику")
@router.message(Command('statistics'))
async def cmd_stat(message : types.Message):
    count_of_right = await get_stat(message.from_user.id)
    part = count_of_right / len(quiz_data)
    text = None
    if part !=0:
        text = f'Вы ответили верно на {part:.0%} вопросов!'
    else:
        text = 'Вы еще не ответили правильно ни на один вопрос!'
    await message.answer(text)
    

