import asyncio
import random
import openai
import json
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from aiogram.dispatcher.filters.builtin import CommandStart
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
import g4f

def ChimeraIsDead(message_log: list, model: str):
    while True:
        try:
            # if model == 'gpt-4':
            response = g4f.ChatCompletion.create(
                model='gpt-4',
                messages=message_log,
                provider=g4f.Provider.ChatgptAi
            )
            # else:
            #     response = g4f.ChatCompletion.create(
            #         model='gpt-3.5-turbo',
            #         messages=message_log,
            #         provider=g4f.Provider.Aichat
            #     )
            if len(str(response)) <= 1:
                pass
            else:
                break
        except KeyError:
            pass
        except:
            pass

    return response

# States
class States(StatesGroup):
    change_custom_lore = State()
class AdminStates(StatesGroup):
    send_message = State()

# Reload JSON data
def reload_data():
    global config, lore_dict, model_dict, buttons
    with open('config.json', 'r', encoding='UTF-8') as f:
        config = json.load(f)

    with open('./db/lore-list.json', 'r', encoding='UTF-8') as f:
        lore_dict = json.load(f)

    with open('./db/model-list.json', 'r', encoding='UTF-8') as f:
        model_dict = json.load(f)

    buttons = {"language": [], "clear": [], "lore": [], "model": []}

    with open('./db/locale.json', 'r', encoding='UTF-8') as f:
        locs = json.load(f)
        for key in locs.keys():
            if str(key).startswith('button-language'):
                buttons['language'].append(str(locs[key]))
            elif str(key).startswith('button-clear'):
                buttons['clear'].append(str(locs[key]))
            elif str(key).startswith('button-lore'):
                buttons['lore'].append(str(locs[key]))
            elif str(key).startswith('button-model'):
                buttons['model'].append(str(locs[key]))

reload_data()

# Set menu command
startcom = types.bot_command.BotCommand(command='start', description='Restart bot.')

openai.api_key = config['chimera-api']
openai.api_base = "https://chimeragpt.adventblocks.cc/api/v1"
character_limit = config['character_limit']

Languages = config['languages']

bot = Bot(config['bot-token'])
dp = Dispatcher(bot, storage=MemoryStorage())

# Localize string
def getlocalized(line: str, lang: str):
    with open('./db/locale.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    try: return data[str(line + '-' + lang[0:2].upper())]
    except:
        try: return data[str(line + '-' + 'EN')]
        except: return 'Failed to translate.'

def timestamp():
    current_time = datetime.now()
    return current_time.timestamp()

# Get total & new users this week or today
def getUserStats():
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    stats = {'ALL': len(data), 'TODAY': 0, "WEEK": 0}

    for user in data:
        try:
            time = data[str(user)]['timestamp']
            now = timestamp()

            if now - 86400 <= time:
                stats['TODAY'] += 1
                if now - 604800 <= time:
                    stats['WEEK'] += 1

        except: pass

    return stats


# Check if user in database & return his settings
def getUser(user_id: str, username = 'None'):
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

        try:
            user = data[str(user_id)]
        except:
            data[str(user_id)] = {}

        if 'lang' not in data[str(user_id)]:
            data[str(user_id)]['lang'] = config['default-language']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        language = data[str(user_id)]['lang']

        if 'lore' not in data[str(user_id)]:
            data[str(user_id)]['lore'] = config['default-lore']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        lore = data[str(user_id)]['lore']

        if 'model' not in data[str(user_id)]:
            data[str(user_id)]['model'] = config['default-model']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        model = data[str(user_id)]['model']

        if 'custom-lore' not in data[str(user_id)]:
            data[str(user_id)]['custom-lore'] = f'My username is @{username}'
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        custom_lore = data[str(user_id)]['custom-lore']

        if 'timestamp' not in data[str(user_id)]:
            data[str(user_id)]['timestamp'] = timestamp()
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

    return (language, lore, model, custom_lore)

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await bot.set_my_commands(commands=[startcom])
    with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
        data = json.load(log)
        data[str(message.from_user.id)] = []
    with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
        json.dump(data, log)
    sticker = random.choice(config['start-stickers'])

    language, lore, model, custom_lore = getUser(message.from_user.id, message.from_user.username)


    if '?' in lore:
        lore = '📑 ' + lore.split('?')[0] + ' > ' +  lore.split('?')[1]

    menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    menu.row(KeyboardButton(text=str(getlocalized('button-clear', language))))
    menu.row(
        KeyboardButton(text=str(getlocalized("button-language", language))),
        KeyboardButton(text=str(getlocalized("button-lore", language))),
        KeyboardButton(text=str(getlocalized("button-model", language)))
    )
    await state.update_data(proccess=False)
    await bot.send_sticker(message.from_user.id, sticker)
    await bot.send_message(message.from_user.id, str(getlocalized('start-menu', language)).format(language=language, model=model, lore=lore), reply_markup=menu)

# Reload JSON dict without restaring bot
@dp.message_handler(commands=['reload'])
async def reloadjson(message: types.Message, state: FSMContext):
    reload_data()
    await message.answer('✅')

# Bot stats
@dp.message_handler(commands=['stats'])
async def botstats(message: types.Message, state: FSMContext):
    stats = getUserStats()
    await message.answer(f'Total users: {stats["ALL"]}\nNew users\n* Week: {stats["WEEK"]}\n* Today: {stats["TODAY"]}')

# Send message to all bot users
@dp.message_handler(commands=['send'])
async def sendcommand(message: types.Message, state: FSMContext):
    if message.from_user.id == config['admin-id']:
        await AdminStates.send_message.set()
        await message.reply('📝 Введите сообщение для отправки.')

@dp.message_handler(state=AdminStates.send_message)
async def send(message: types.Message, state: FSMContext):
    if message.from_user.id == config['admin-id']:
        await state.update_data(send=message.text)
        menu = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='✅', callback_data='send'), InlineKeyboardButton(text='⛔', callback_data='cancel'))
        await message.reply(f'Вот так будет выглядеть рассылка, начать отправку?\n\n{message.text}', reply_markup=menu)

@dp.callback_query_handler(state=AdminStates.send_message)
async def callback(call: CallbackQuery, state: FSMContext):
    if call.data == 'send':
        msg = await state.get_data()
        msg = msg['send']
        await state.finish()
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            index = 0
            stats = await bot.send_message(call.from_user.id, f'0 / {len(data)}')
            for user in data.keys():
                try:
                    await bot.send_message(chat_id=int(user), text=msg)
                    index+=1
                    await bot.edit_message_text(message_id=stats['message_id'], chat_id=call.from_user.id, text=f'{index} / {len(data)}')
                    await asyncio.sleep(0.13)
                except: pass
            await bot.edit_message_text(message_id=stats['message_id'], chat_id=call.from_user.id,
                                        text=f'🏁 {index} / {len(data)}')
    if call.data == 'cancel':
        await state.finish()


# Chat message handler
@dp.message_handler()
async def chat(message: types.Message, state: FSMContext):
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    language, lore, model, custom_lore = getUser(message.from_user.id, message.from_user.username)

    if message.text in buttons['clear'] and list(message.text).count(' ') <= 2:
        if '?' in lore:
            lore = '📑 ' + lore.split('?')[0] + ' > ' + lore.split('?')[1]
        await message.reply(str(getlocalized('start-menu', language)).format(language=language, model=model, lore=str(data[str(message.from_user.id)]['lore']).replace('?', ' > ')))
        with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
            data = json.load(log)
            data[str(message.from_user.id)] = []
        with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
            json.dump(data, log)
    elif message.text in buttons['language'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=1)
        global Languages
        for lang in Languages:
            menu.add(InlineKeyboardButton(text=lang + (' ✅' if language == lang else ''), callback_data=f'lang-to>{lang}'))
        await message.reply(getlocalized('current', language).format(language), reply_markup=menu)
    elif message.text in buttons['lore'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=1)
        for lore in lore_dict.keys():
            if type(lore_dict[lore]) is dict:
                menu.add(InlineKeyboardButton(
                    text=lore, callback_data=f'lore-page>{lore}'))
            else:
                menu.add(InlineKeyboardButton(text=lore + (' ✅' if lore == str(data[str(message.from_user.id)]['lore']) else ''), callback_data=f'lore-to>{lore}'))
        menu.add(InlineKeyboardButton(text='Custom' + (' ✅' if 'custom' == str(data[str(message.from_user.id)]['lore']) else ''), callback_data=f'lore-to>custom'))
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            await message.reply(getlocalized('current', language).format(str(data[str(message.from_user.id)]['lore']).replace('?', ' > ')), reply_markup=menu)
    elif message.text in buttons['model'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=2)
        for model in model_dict['text-models']:
            menu.add(InlineKeyboardButton(text=model + (' ✅' if model == str(data[str(message.from_user.id)]['model']) else ''), callback_data=f'model-to>{model}'))
        await message.reply(getlocalized('current', language).format(str(data[str(message.from_user.id)]['model'])), reply_markup=menu)
    else:
        await message.answer_chat_action("typing")
        await state.update_data(proccess=True)
        message_log = [
            {"role": "system", "content": lore.format(language)},
        ]

        with open('./db/message-log.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            try:
                messages = data[str(message.from_user.id)]
            except: messages = []

        for msg in messages:
            message_log.append(msg)
        message_log.append({"role": "user", "content": message.text})

        total_characters = sum(len(message['content'])
                               for message in message_log)
        while total_characters > character_limit and len(message_log) > 1:
            print(
                f"total_characters {total_characters} exceed limit of {character_limit}, removing oldest message")
            total_characters -= len(message_log[1]["content"])
            message_log.pop(1)

        response = None
        response = ChimeraIsDead(message_log, model)
            # return await message.answer(getlocalized('try-later', language))

        # for answer in response['choices']:
        message_log.append({"role": "assistant", "content": response})
        with open('./db/message-log.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            message_log.pop(0)
            data[str(message.from_user.id)] = message_log
        with open('./db/message-log.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f)
        await message.answer(response)

        await state.update_data(proccess=False)

@dp.callback_query_handler()
async def callback(call: CallbackQuery, state: FSMContext):
    await call.answer('⌛...')
    if call.data.startswith('lang-to'):
        lang = call.data.split('>')[1]
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
            try:
                data[str(call.from_user.id)]['lang'] = lang
            except:
                data[str(call.from_user.id)] = {}; data[str(call.from_user.id)]['lang'] = lang
            json.dump(data, f)
        sticker = random.choice(config['start-stickers'])

        language, lore, model, custom_lore = getUser(call.from_user.id, call.from_user.username)

        menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        menu.row(KeyboardButton(text=str(getlocalized('button-clear', language))))
        menu.row(
            KeyboardButton(text=str(getlocalized("button-language", language))),
            KeyboardButton(text=str(getlocalized("button-lore", language))),
            KeyboardButton(text=str(getlocalized("button-model", language)))
        )
        await bot.send_sticker(call.from_user.id, sticker)
        await bot.send_message(call.from_user.id,
                               str(getlocalized('start-menu', language)).format(language=language, model=model,
                                                                                lore=lore), reply_markup=menu)

    elif call.data.startswith('lore-to'):
        with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
            data = json.load(log)
            data[str(call.from_user.id)] = []
        with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
            json.dump(data, log)

        lore = call.data.split('>')[1]

        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
            try:
                data[str(call.from_user.id)]['lore'] = lore
            except:
                data[str(call.from_user.id)] = {};
                data[str(call.from_user.id)]['lore'] = lore
            json.dump(data, f)

        if '?' in lore:
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='ℹ️', callback_data=f'about-lore>{lore}'))
            await bot.send_message(call.from_user.id, lore.split('?')[1], reply_markup=menu)
        elif lore != 'custom':
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='ℹ️', callback_data=f'about-lore>{lore}'))
            await bot.send_message(call.from_user.id, lore, reply_markup=menu)
        else:
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='✏️', callback_data=f'change-custom-lore'),
                InlineKeyboardButton(text='ℹ️️', callback_data=f'about-lore>custom'),
            )
            await bot.send_message(call.from_user.id, lore, reply_markup=menu)

    elif call.data.startswith('lore-page>'):
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)

        lore = call.data.split('>')[1]

        menu = InlineKeyboardMarkup(row_width=2)
        for lre in lore_dict[lore].keys():
            try:
                menu.add(InlineKeyboardButton(text=lre + (' ✅' if lre == str(data[str(call.from_user.id)]['lore']).split('?')[1] else ''), callback_data=f'lore-to>{lore}?{lre}'))
            except: menu.add(InlineKeyboardButton(text=lre, callback_data=f'lore-to>{lore}?{lre}'))
        await bot.send_message(call.from_user.id, lore, reply_markup=menu)

    elif call.data.startswith('change-custom-lore'):
        await States.change_custom_lore.set()
        await bot.send_message(call.from_user.id, '✍ Write new custom lore:')

    elif call.data.startswith('about-lore'):
        lore = call.data.split('>')[1]
        if lore == 'custom':
            with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
                data = json.load(f)
                loredata = data[str(call.from_user.id)]['custom-lore']
            return await bot.send_message(call.from_user.id, f'ℹ️ {lore}:\n{loredata}')
        if '?' in lore:
            loredata = lore_dict[f'{lore.split("?")[0]}'][f'{lore.split("?")[1]}']
            return await bot.send_message(call.from_user.id, f'ℹ️ {lore}:\n{loredata}')
        await bot.send_message(call.from_user.id, f'ℹ️ {lore}:\n{lore_dict[lore]}')

    elif call.data.startswith('model-to'):
        with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
            data = json.load(log)
            data[str(call.from_user.id)] = []
        with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
            json.dump(data, log)

        model = call.data.split('>')[1]
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
            try:
                data[str(call.from_user.id)]['model'] = model
            except:
                data[str(call.from_user.id)] = {};
                data[str(call.from_user.id)]['model'] = model
            json.dump(data, f)
        await bot.send_message(call.from_user.id, model)

@dp.message_handler(state=States.change_custom_lore)
async def changecustomlore(message: types.message, state: FSMContext):
    await state.finish()
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
        try:
            data[str(message.from_user.id)]['custom-lore'] = message.text
        except:
            data[str(message.from_user.id)] = {};
            data[str(message.from_user.id)]['custom-lore'] = message.text
        json.dump(data, f)
    await message.reply('✅')

# Start bot
executor.start_polling(dp, skip_updates=True)