from utils.bot import bot
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


dp = Dispatcher(bot, storage=MemoryStorage())


if __name__ == '__main__':
    import handlers.admin
    handlers.admin.setup(dp)
    import handlers.commands
    handlers.commands.setup(dp)
    import handlers.query
    handlers.query.setup(dp)
    import handlers.chatgpt
    handlers.chatgpt.setup(dp)
    executor.start_polling(dp, skip_updates=True)
