import asyncio
import os
import threading
import aiogram
from utils.imports.imports import *


async def chat(message: types.Message, state: FSMContext):
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    language, lore, model, custom_lore = await getUser(message.from_user.id, message.from_user.username)

    if message.text in buttons['clear'] and list(message.text).count(' ') <= 2:
        if '?' in lore:
            lore = '📑 ' + lore.split('?')[0] + ' > ' + lore.split('?')[1]
        await message.reply(
            formatter(str(await getlocalized('start-menu', language)), language=language,
                   model=model, custom_lore=custom_lore, user=message.from_user,
                   lore=str(data[str(message.from_user.id)]['lore']).replace('?', ' > ')), reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='Discord', url='https://discord.gg/5HWuxxsJjn')))

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
        await message.reply(str(await getlocalized('current', language)).format(language), reply_markup=menu)
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
            await message.reply(str(await getlocalized('current', language)).format(str(data[str(message.from_user.id)]['lore']).replace('?', ' > ')), reply_markup=menu)
    elif message.text in buttons['model'] and list(message.text).count(' ') <= 2:
        menu = InlineKeyboardMarkup(row_width=2)
        for model in model_dict['text-models']:
            menu.add(InlineKeyboardButton(text=model + (' ✅' if model == str(data[str(message.from_user.id)]['model']) else ''), callback_data=f'model-to>{model}'))
        await message.reply(str(await getlocalized('current', language)).format(str(data[str(message.from_user.id)]['model'])), reply_markup=menu)
    else:
        try:
            if (await state.get_data())['proccess'] is True:
                msg = await message.answer('⏳')
                await asyncio.sleep(3)
                return await msg.delete()
        except: pass
        await message.answer_chat_action("typing")
        await state.update_data(proccess=True)
        threading.Thread(target=run_background_task, args=(lore, language, message, model, state)).start()
        print(True)


async def background_task(lore, language, message, model, state):
    await answer_gpt(lore, language, message, model, state)


def run_background_task(lore, language, message, model, state):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(background_task(lore, language, message, model, state))


# DB Lock - So my message-log.json file won't die lol.
db_lock = threading.Lock()


def update_message_log(message_log, message):
    with db_lock:
        with open('./db/message-log.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            message_log.pop(0)
            data[str(message.from_user.id)] = message_log
        with open('./db/message-log.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f)


async def answer_gpt(lore, language, message, model, state):
    message_log = [
        {"role": "system", "content": str(await getLore(lore)).format(language)},
    ]

    with open('./db/message-log.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
        try:
            messages = data[str(message.from_user.id)]
        except:
            messages = []

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
    # print(message_log)
    response = await chatgpt._generate_response_async(message_log, model)
    # return await message.answer(getlocalized('try-later', language))

    # for answer in response['choices']:
    message_log.append({"role": "assistant", "content": response})
    update_message_log(message_log, message)

    load_dotenv()
    bot = aiogram.Bot(os.getenv('token'))


    try:
        await bot.send_message(message.from_user.id, str(response).replace('_', '\_').replace('*', '\*').replace('[', '\[').replace(']', '\]').replace('(', '\(').replace(')', '\)').replace('~', '\~').replace('<', '\<').replace('>', '\>').replace('#', '\#').replace('+', '\+').replace('-', '\-').replace('=', '\=').replace('|', '\|').replace('{', '\{').replace('}', '\}').replace('.', '\.').replace('!', '\!'), parse_mode='markdownv2')
    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, str(response))
    await state.update_data(proccess=False)
    await (await bot.get_session()).close()


def setup(dp: Dispatcher):
    dp.register_message_handler(chat, content_types=['text'], state=None)
