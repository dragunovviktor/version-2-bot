from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from Parser import Parser

router = Router()

# Команда /start
@router.message(F.command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Все расписание", callback_data="full_schedule"),
                InlineKeyboardButton(text="Неделя", callback_data="week_schedule"),
            ],
            [
                InlineKeyboardButton(text="Следующая неделя", callback_data="next_week"),
                InlineKeyboardButton(text="Другая кнопка", callback_data="other_button"),
            ],
        ]
    )

    await message.answer(
        "Привет! Выбери действие ниже:",
        reply_markup=keyboard
    )

# Обработчик нажатий на кнопки
@router.callback_query()
async def handle_callback(callback: CallbackQuery):
    action = callback.data

    if action == "full_schedule":
        await send_full_schedule(callback.message)
    elif action == "week_schedule":
        await send_schedule_for_week(callback.message)
    elif action == "next_week":
        await callback.message.answer("Расписание на следующую неделю пока не добавлено.")
    elif action == "other_button":
        await callback.message.answer("Это другая кнопка.")
    else:
        await callback.message.answer("Неизвестное действие.")

# Отправка полного расписания
async def send_full_schedule(message: Message):
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

# Отправка расписания на неделю
async def send_schedule_for_week(message: Message):
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)

        # Собираем расписание за последние 7 дней
        all_schedules = []
        for day, schedule in full_schedule.items():
            all_schedules.append((day, schedule))

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
