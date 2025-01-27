import re
from aiogram import Router, F
from aiogram.types import Message
from Parser import Parser
from datetime import datetime

router = Router()

# Регулярное выражение для поиска даты в формате ДД.ММ.ГГГГ
DATE_REGEX = r"\b(\d{2}\.\d{2}\.\d{4})\b"


@router.message(F.command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Отправь одну из следующих команд:\n"
        "- **Все расписание** — чтобы получить полное расписание\n"
        "- **Неделя** — чтобы получить расписание на последнюю неделю\n"
        "- Введи дату в формате ДД.ММ.ГГГГ — чтобы получить расписание на конкретный день"
    )


@router.message(F.text)
async def handle_message(message: Message):
    text = message.text.strip().lower()

    # Если пользователь хочет получить полное расписание
    if text == "все расписание":
        await send_full_schedule(message)

    # Если пользователь хочет получить расписание на последнюю неделю
    elif text == "неделя":
        await send_schedule_for_week(message)

    # Если пользователь вводит дату для получения расписания
    elif re.match(r"\d{2}\.\d{2}\.\d{4}", text):
        await send_schedule_for_date(text, message)

    else:
        await message.answer(
            "Я не понимаю эту команду. Пожалуйста, выбери одну из команд или введи дату в формате ДД.ММ.ГГГГ.")


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

        # Разбиваем длинное сообщение на части
        await send_message_in_parts(message, response)
        await send_commands(message)  # Отправляем доступные команды
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

        # Разбиваем длинное сообщение на части
        await send_message_in_parts(message, response)
        await send_commands(message)  # Отправляем доступные команды
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")


async def send_schedule_for_date(date_str: str, message: Message):
    """
    Отправить расписание для указанной даты.
    Использует регулярное выражение для поиска даты в расписании.
    """
    parser = Parser(Parser.url)
    soup = parser.parse()

    if soup:
        full_schedule = parser.extract_schedule(soup)

        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return

        date_str = date_obj.strftime("%d.%m.%Y")

        found_schedule = []
        for day, schedule in full_schedule.items():
            if re.search(DATE_REGEX, day):
                match = re.search(DATE_REGEX, day)
                if match:
                    found_date = match.group(1)
                    if found_date == date_str:
                        found_schedule.append((day, schedule))

        if found_schedule:
            response = f"📅 Расписание на {date_str}:\n"
            for day, schedule in found_schedule:
                for item in schedule:
                    time = item['time']
                    subject = item['subject']
                    response += f"🕒 {time} - {subject}\n"
            # Разбиваем длинное сообщение на части
            await send_message_in_parts(message, response)
            await send_commands(message)  # Отправляем доступные команды
        else:
            await message.answer("Нет расписания на эту дату.")
    else:
        await message.answer("Не удалось загрузить расписание. Попробуйте позже.")


async def send_message_in_parts(message: Message, text: str):
    """
    Разбивает длинное сообщение на части и отправляет их по очереди.
    """
    # Разбиваем текст на части по 4096 символов
    part_size = 4096
    for i in range(0, len(text), part_size):
        await message.answer(text[i:i + part_size])


async def send_commands(message: Message):
    """
    Отправить сообщение с доступными командами.
    """
    commands = (
        "Доступные команды:\n"
        "- **Все расписание** — чтобы получить полное расписание\n"
        "- **Неделя** — чтобы получить расписание на последнюю неделю\n"
        "- Введи дату в формате ДД.ММ.ГГГГ — чтобы получить расписание на конкретный день"
    )
    await message.answer(commands)
