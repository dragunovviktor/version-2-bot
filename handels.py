from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from Parser import Parser

router = Router()

@router.message(F.command("start"))
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Все расписание")],
            [KeyboardButton(text="Неделя")],
            [KeyboardButton(text="Другая кнопка")],
        ],
        resize_keyboard=True  # Прямоугольные кнопки
    )

    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы получить все расписание или расписание на неделю:",
        reply_markup=keyboard
    )

# Обработка команды в любом чате
@router.message(F.text)
async def handle_message(message: Message):
    if not message.text:  # Проверка на наличие текста
        await message.answer("Сообщение не содержит текста.")
        return

    text = message.text.lower()
    print(f"Получен текст: {text}")  # Логируем текст

    # Если это группа, то не отвечаем на обычные сообщения
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if text not in ["все расписание", "неделя", "другая кнопка"]:
            return  # Если текст не является командой, не реагируем

    # Если сообщение относится к команде
    if text == "все расписание":
        await send_full_schedule(message)
    elif text == "неделя":
        await send_schedule_for_week(message)
    elif text == "другая кнопка":
        await message.answer("Это сообщение для другой кнопки.")
    else:
        await message.answer("Я не понимаю эту команду. Выбери кнопку ниже.")

# Обработчик для личных сообщений
@router.message(F.chat.type == "private")
async def private_message_handler(message: Message):
    """
    Обработка сообщений из личных чатов.
    """
    await handle_message(message)

# Обработчик для сообщений в группах
@router.message(F.chat.type == "group")
async def group_message_handler(message: Message):
    """
    Обработка сообщений из групп.
    """
    # Бот не должен отвечать на сообщения, если они не соответствуют команде
    text = message.text.lower()
    if text not in ["все расписание", "неделя", "другая кнопка"]:
        return  # Не отвечаем на обычные сообщения

    await handle_message(message)

async def send_full_schedule(message: Message):
    """
    Отправить все расписание.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)
        response = "📅 Полное расписание:\n\n"

        for day, schedule in full_schedule.items():
            response += f"📅 **{day}**\n"
            for item in schedule:
                time = item['time']
                subject = item['subject']
                response += f"🕒 {time} - {subject}\n"
            response += "\n"

            # Отправляем сообщения по частям, если они слишком длинные
            if len(response) > 3000:
                await message.answer(response)
                response = ""

        if response:
            await message.answer(response)
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")

async def send_schedule_for_week(message: Message):
    """
    Отправить последние 7 дней расписания.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)
        
        # Собираем все расписание в один список
        all_schedules = []
        for day, schedule in full_schedule.items():
            all_schedules.append((day, schedule))

        # Получаем последние 7 дней
        last_7_days = all_schedules[-7:]

        response = "📅 Расписание на последние 7 дней:\n\n"
        for day, schedule in last_7_days:
            response += f"📅 **{day}**\n"
            for item in schedule:
                time = item['time']
                subject = item['subject']
                response += f"🕒 {time} - {subject}\n"
            response += "\n"

        # Отправляем сообщения по частям, если они слишком длинные
        if len(response) > 3000:
            await message.answer(response)
            response = ""

        if response:
            await message.answer(response)
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")

