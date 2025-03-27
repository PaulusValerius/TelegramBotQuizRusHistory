from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
quiz_data = None

#создает клавиатуру с коллбэками на вопрос.
def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

#Получает номер вопроса из БД.Получает вопрос из переменной quiz_data. 
# Создает клавиатуру для текущего вопроса  
async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

#Функция обнуляет значения в БД при начале нового опроса. И выводит вопрос.
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

#Запрос в БД для получения индекса вопроса.
async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;
        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    

#Запрос в БД для получения статистики. 
#Количество правильных ответов содержится в столбце сount_of_righ БД
async def get_stat(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;
        SELECT count_of_right
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]["count_of_right"] is None:
        return 0
    return results[0]["count_of_right"]

# Обновляет информацию в БД. 
# зависит от параметров mode и start. Если mode, то отправляет в БД запрос на полное 
# обновление строки или вставку новой. Этот запрос исполбзуется для обнуления данных квиза при новом опросе.
# Если not mode, то обновляет текущую информацию в БД. При этом если start 
# не None то обновляет и индекс текущего вопроса и количество верных ответов. Наоборот обновляет 
# только индекс текущего вопроса. 
async def update_quiz_index(user_id, question_index, mode = True, start = None):
    if mode:
        set_quiz_state = f"""
            DECLARE $user_id AS Uint64;
            DECLARE $question_index AS Uint64;
            UPSERT INTO `quiz_state` (`user_id`, `question_index`, `count_of_right`)
            VALUES ($user_id, $question_index, 0);
        """
        execute_update_query(
            pool,
            set_quiz_state,
            user_id=user_id,
            question_index=question_index,
        )
    else:
        set_quiz_state = None
        if start is None:
            set_quiz_state = f"""
                DECLARE $user_id AS Uint64;
                DECLARE $question_index AS Uint64;
                DECLARE $count_of_right AS Uint64;
                UPDATE `quiz_state`
                SET 
                question_index = {question_index},
                count_of_right = count_of_right + 1
                WHERE user_id = {user_id}
            """
        else:
            set_quiz_state = f"""
                DECLARE $user_id AS Uint64;
                DECLARE $question_index AS Uint64;
                DECLARE $count_of_right AS Uint64;
                UPDATE `quiz_state`
                SET 
                question_index = {question_index}
                WHERE user_id = {user_id}
            """
        execute_update_query(
            pool,
            set_quiz_state,
        )
        
