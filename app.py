import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handels import router

async def main():
    # Укажите ваш токен
    TOKEN_API = '7824936199:AAHO8j-aGUszBF2_gibOV0tD_V5KzDsacfs'
    bot = Bot(token=TOKEN_API)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    
    # Получаем username бота (важно для работы в группах)
    bot_info = await bot.get_me()
    print(f"Запущен бот @{bot_info.username}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')

