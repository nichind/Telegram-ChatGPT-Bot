from utils.imports.imports import *


async def start(message: types.Message, state: FSMContext):
    #await bot.send_message(config['log-chat-id'], f"User Started @{message.from_user.username} - {message.from_user.full_name}")
    with open('./db/message-log.json', 'r', encoding='UTF-8') as log:
        data = json.load(log)
        data[str(message.from_user.id)] = []
    with open('./db/message-log.json', 'w', encoding='UTF-8') as log:
        json.dump(data, log)
    sticker = random.choice(config['start-stickers'])

    language, lore, model, custom_lore = await getUser(message.from_user.id, message.from_user.username)

    if '?' in lore:
        lore = '📑 ' + lore.split('?')[0] + ' > ' +  lore.split('?')[1]

    menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    menu.row(KeyboardButton(text=str(await getlocalized('button-clear', language))))
    menu.row(
        KeyboardButton(text=str(await getlocalized("button-language", language))),
        KeyboardButton(text=str(await getlocalized("button-lore", language))),
        KeyboardButton(text=str(await getlocalized("button-model", language)))
    )
    await state.update_data(proccess=False)
    await bot.send_sticker(message.from_user.id, sticker, reply_markup=menu)
    await bot.send_message(message.from_user.id, str(await getlocalized('start-menu', language)).format(language=language, model=model, lore=lore),
                           reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='Discord', url='https://discord.gg/5HWuxxsJjn')))


async def botstats(message: types.Message, state: FSMContext):
    stats = await getUserStats()
    await message.answer(f'Total users: {stats["ALL"]}\nNew users\n* Week: {stats["WEEK"]}\n* Today: {stats["TODAY"]}')


async def changecustomlore(message: types.message, state: FSMContext):
    await state.finish()
    with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    with open('./db/user-settings.json', 'w', encoding='UTF-8') as f:
        try:
            data[str(message.from_user.id)]['custom-lore'] = message.text
        except:
            data[str(message.from_user.id)] = {}
            data[str(message.from_user.id)]['custom-lore'] = message.text
        json.dump(data, f)
    await message.reply('✅')

def setup(dp: Dispatcher):
    dp.register_message_handler(start, content_types=['text'], state='*', commands=['start'])
    dp.register_message_handler(botstats, content_types=['text'], state='*', commands=['stats'])
    dp.register_message_handler(changecustomlore, content_types=['text'], state=States.change_custom_lore)
