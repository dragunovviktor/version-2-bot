from datetime import datetime, timedelta
import requests
import chardet
from bs4 import BeautifulSoup
import re

class Parser:
    url = 'https://rasp.pskgu.ru/groups/029204.html'

    def __init__(self, url=None):
        if url:
            self.url = url

    def parse(self):
        """
        Загружает HTML-страницу по указанному URL и возвращает объект BeautifulSoup.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            detected_encoding = chardet.detect(response.content)['encoding']
            return BeautifulSoup(response.content.decode(detected_encoding), 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def extract_schedule(self, soup):
        """
        Извлекает расписание из HTML-страницы.
        """
        days_schedule = {}
        rows = soup.select('.week .table tbody tr')

        current_day = None

        for row in rows:
            cells = row.find_all('td')

            if len(cells) == 0:
                continue

            day = cells[0].get_text(strip=True)
            if day:
                current_day = day
                days_schedule[current_day] = []

            for i in range(1, len(cells)):
                time = cells[0].get_text(strip=True) if i == 1 else ''
                subject = cells[i].get_text(strip=True) if cells[i].get_text(strip=True) else f"{i}-я пара (отсутствует)"
                teacher = ''
                additional_info = ''

                subject = self.format_subject(subject)

                if subject != f"{i}-я пара (отсутствует)":
                    teacher = "Не указан"
                    additional_info = "Информация отсутствует"

                days_schedule[current_day].append({
                    'time': time,
                    'subject': subject,
                    'teacher': teacher,
                    'additional_info': additional_info
                })

        return days_schedule

    def format_subject(self, subject):
        """
        Форматирует название предмета, добавляя пробелы между словами на разных языках.
        """
        formatted_subject = re.sub(r'([a-zа-я])([A-ZА-Я])', r'\1 \2', subject)
        return formatted_subject

    def get_schedule_for_date(self, date):
        """
        Получает расписание для указанной даты.
        """
        date_obj = datetime.strptime(date, "%d.%m.%Y")
        day_of_week = date_obj.strftime('%A')
        soup = self.parse()
        if soup:
            schedule = self.extract_schedule(soup)
            if day_of_week in schedule:
                return schedule[day_of_week]
        return None

    def get_schedule_for_next_days(self, days_ahead=7):
        """
        Получает расписание на следующие дни.
        """
        current_date = datetime.now()
        next_schedule = {}

        for i in range(days_ahead):
            future_date = current_date + timedelta(days=i)
            future_date_str = future_date.strftime('%d.%m.%Y')
            day_of_week = future_date.strftime('%A')

            schedule = self.get_schedule_for_date(future_date_str)
            if schedule:
                next_schedule[future_date_str] = schedule
            else:
                next_schedule[future_date_str] = "Занятий нет"
        return next_schedule

    def extract_dates_from_lister(self, lister):
        """
        Извлекает уникальные даты из lister с помощью регулярных выражений.
        """
        date_pattern = r'\b\d{2}\.\d{2}\.\d{4}\b'  # Шаблон для поиска дат формата dd.mm.yyyy
        dates = set()

        for item in lister:
            found_dates = re.findall(date_pattern, item)
            if found_dates:
                dates.update(found_dates)

        return sorted(dates)

