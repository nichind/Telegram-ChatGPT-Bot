import random

import openai
import json
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

class States(StatesGroup):
    change_custom_lore = State()

with open('config.json', 'r', encoding='UTF-8') as f:
    config = json.load(f)

with open('./db/lore-list.json', 'r', encoding='UTF-8') as f:
    lore_dict = json.load(f)

with open('./db/model-list.json', 'r', encoding='UTF-8') as f:
    model_dict = json.load(f)

openai.api_key = config['chimera-api']
openai.api_base = "https://chimeragpt.adventblocks.cc/v1"
character_limit = config['character_limit']

Languages = config['languages']

bot = Bot(config['bot-token'])
dp = Dispatcher(bot, storage=MemoryStorage())

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

def getlocalized(line: str, lang: str):
    with open('./db/locale.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    try: return data[str(line + '-' + lang[0:2].upper())]
    except:
        try: return data[str(line + '-' + 'EN')]
        except: return 'Failed to translate.'


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
        data = json.load(log)
        data[str(message.from_user.id)] = []
    with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
        json.dump(data, log)
    sticker = random.choice(config['start-stickers'])

    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
        try: user = data[str(message.from_user.id)]
        except: data[str(message.from_user.id)] = {}

        if 'lang' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['lang'] = config['default-language']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        language = data[str(message.from_user.id)]['lang']

        if 'lore' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['lore'] = config['default-lore']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        lore = data[str(message.from_user.id)]['lore']

        if 'model' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['model'] = config['default-model']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        model = data[str(message.from_user.id)]['model']

        if 'custom-lore' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['custom-lore'] = f'My username is @{message.from_user.username}'
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        custom_lore = data[str(message.from_user.id)]['custom-lore']

    menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    menu.row(KeyboardButton(text=str(getlocalized('button-clear', language))))
    menu.row(
        KeyboardButton(text=str(getlocalized("button-language", language))),
        KeyboardButton(text=str(getlocalized("button-lore", language))),
        KeyboardButton(text=str(getlocalized("button-model", language)))
    )
    await bot.send_sticker(message.from_user.id, sticker)
    await bot.send_message(message.from_user.id, str(getlocalized('start-menu', language)).format(language=language, model=model, lore=lore), reply_markup=menu)

@dp.message_handler()
async def chat(message: types.Message, state: FSMContext):
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
        try:
            user = data[str(message.from_user.id)]
        except:
            data[str(message.from_user.id)] = {}

        if 'lang' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['lang'] = config['default-language']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        language = data[str(message.from_user.id)]['lang']

        if 'lore' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['lore'] = config['default-lore']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        if data[str(message.from_user.id)]['lore'] != 'custom':
            lore = lore_dict[str(data[str(message.from_user.id)]['lore'])]

        if 'model' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['model'] = config['default-model']
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        model = data[str(message.from_user.id)]['model']

        if 'custom-lore' not in data[str(message.from_user.id)]:
            data[str(message.from_user.id)]['custom-lore'] = f'My username is @{message.from_user.username}'
            with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)

        custom_lore = data[str(message.from_user.id)]['custom-lore']

    if message.text in buttons['clear'] and list(message.text).count(' ') <= 1:
        await message.reply(str(getlocalized('start-menu', language)).format(language=language, model=model, lore=str(data[str(message.from_user.id)]['lore'])))
        with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
            data = json.load(log)
            data[str(message.from_user.id)] = []
        with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
            json.dump(data, log)
    elif message.text in buttons['language'] and list(message.text).count(' ') <= 1:
        menu = InlineKeyboardMarkup(row_width=1)
        global Languages
        for lang in Languages:
            menu.add(InlineKeyboardButton(text=lang, callback_data=f'lang-to>{lang}'))
        await message.reply(getlocalized('current', language).format(language), reply_markup=menu)
    elif message.text in buttons['lore'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=1)
        for lore in lore_dict.keys():
            menu.add(InlineKeyboardButton(text=lore, callback_data=f'lore-to>{lore}'))
        menu.add(InlineKeyboardButton(text='Custom', callback_data=f'lore-to>custom'))
        await message.reply(getlocalized('current', language).format(lore), reply_markup=menu)
    elif message.text in buttons['model'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=1)
        for model in model_dict['text-models']:
            menu.add(InlineKeyboardButton(text=model, callback_data=f'model-to>{model}'))
        await message.reply(getlocalized('current', language).format(model), reply_markup=menu)
    else:

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
        print(message_log)
        response = None
        try:
            response = openai.ChatCompletion.create(
                model=str(model),
                messages=message_log
            )
        except: return await message.answer('Error...')

        for answer in response['choices']:
            message_log.append({"role": "assistant", "content": answer['message']['content']})
            with open('./db/message-log.json', 'r', encoding='UTF-8') as f:
                data = json.load(f)
                message_log.pop(0)
                data[str(message.from_user.id)] = message_log
            with open('./db/message-log.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)
            await message.answer(answer['message']['content'])

@dp.callback_query_handler()
async def callback(call: CallbackQuery, state: FSMContext):
    if call.data.startswith('lang-to>'):
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

        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            try:
                user = data[str(call.from_user.id)]
            except:
                data[str(call.from_user.id)] = {}

            if 'lang' not in data[str(call.from_user.id)]:
                data[str(call.from_user.id)]['lang'] = config['default-language']
                with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                    json.dump(data, f)

            language = data[str(call.from_user.id)]['lang']

            if 'lore' not in data[str(call.from_user.id)]:
                data[str(call.from_user.id)]['lore'] = config['default-lore']
                with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                    json.dump(data, f)

            lore = data[str(call.from_user.id)]['lore']

            if 'model' not in data[str(call.from_user.id)]:
                data[str(call.from_user.id)]['model'] = config['default-model']
                with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                    json.dump(data, f)

            model = data[str(call.from_user.id)]['model']

            if 'custom-lore' not in data[str(call.from_user.id)]:
                data[str(call.from_user.id)]['custom-lore'] = f'My username is @{call.from_user.username}'
                with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
                    json.dump(data, f)

            custom_lore = data[str(call.from_user.id)]['custom-lore']

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

    elif call.data.startswith('lore-to>'):
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

        if lore != 'custom':
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='ℹ️', callback_data=f'about-lore>{lore}'))
            await bot.send_message(call.from_user.id, lore, reply_markup=menu)
        else:
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='✏️', callback_data=f'change-custom-lore'),
                InlineKeyboardButton(text='ℹ️️', callback_data=f'about-lore>custom'),
            )
            await bot.send_message(call.from_user.id, lore, reply_markup=menu)

    elif call.data.startswith('change-custom-lore'):
        await States.change_custom_lore.set()
        await bot.send_message(call.from_user.id, '✍ Write new custom lore:')

    elif call.data.startswith('about-lore>'):
        lore = call.data.split('>')[1]
        if lore == 'custom':
            with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
                data = json.load(f)
                loredata = data[str(call.from_user.id)]['custom-lore']
            return await bot.send_message(call.from_user.id, f'ℹ️ {lore}:\n{loredata}')
        await bot.send_message(call.from_user.id, f'ℹ️ {lore}:\n{lore_dict[lore]}')

    elif call.data.startswith('model-to>'):
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

executor.start_polling(dp, skip_updates=True)