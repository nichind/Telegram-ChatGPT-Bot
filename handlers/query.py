from utils.imports.imports import *


# THIS IS FUCKING PAIN, but I won't remake it normally, at least anytime soon...
async def callback(call: CallbackQuery, state: FSMContext):
    await call.answer('⌛...')
    print(call.data)

    if call.data.startswith('lore-main'):
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        menu = InlineKeyboardMarkup(row_width=1)
        for lore in lore_dict.keys():
            if type(lore_dict[lore]) is dict:
                menu.add(InlineKeyboardButton(
                    text=lore, callback_data=f'lore-page>{lore}'))
            else:
                menu.add(InlineKeyboardButton(
                    text=lore + (' ✅' if lore == str(data[str(call.from_user.id)]['lore']) else ''),
                    callback_data=f'lore-to>{lore}'))
        menu.add(InlineKeyboardButton(
            text='Custom' + (' ✅' if 'custom' == str(data[str(call.from_user.id)]['lore']) else ''),
            callback_data=f'lore-to>custom'))
        language, lore, model, custom_lore = await getUser(call.from_user.id, call.from_user.username)
        await call.message.edit_text(str(await getlocalized('current', language)).format(str(data[str(call.from_user.id)]['lore']).replace('?', ' > ')), reply_markup=menu)


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

        language, lore, model, custom_lore = await getUser(call.from_user.id, call.from_user.username)

        menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        menu.row(KeyboardButton(text=str(await getlocalized('button-clear', language))))
        menu.row(
            KeyboardButton(text=str(await getlocalized("button-language", language))),
            KeyboardButton(text=str(await getlocalized("button-lore", language))),
            KeyboardButton(text=str(await getlocalized("button-model", language)))
        )

        await bot.send_sticker(call.from_user.id, sticker)
        await bot.send_message(call.from_user.id,
                               str(await getlocalized('start-menu', language)).format(language=language, model=model,
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
            menu.row(InlineKeyboardButton(text='◀️', callback_data=f'lore-page>{lore.split("?")[0]}'))
            await call.message.edit_text("✅ " + lore.split('?')[1], reply_markup=menu)
        elif lore != 'custom':
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='ℹ️', callback_data=f'about-lore>{lore}'))
            menu.row(InlineKeyboardButton(text='◀️', callback_data=f'lore-main'))
            await call.message.edit_text("✅ " + lore, reply_markup=menu)
        else:
            menu = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text='✏️', callback_data=f'change-custom-lore'),
                InlineKeyboardButton(text='ℹ️️', callback_data=f'about-lore>custom'),
            )
            menu.row(InlineKeyboardButton(text='◀️', callback_data=f'lore-main'))
            await call.message.edit_text("✅ " + lore, reply_markup=menu)

    elif call.data.startswith('lore-page>'):
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)

        lore = call.data.split('>')[1]

        menu = InlineKeyboardMarkup(row_width=2)
        for lre in lore_dict[lore].keys():
            try:
                menu.add(InlineKeyboardButton(text=lre + (' ✅' if lre == str(data[str(call.from_user.id)]['lore']).split('?')[1] else ''), callback_data=f'lore-to>{lore}?{lre}'))
            except: menu.add(InlineKeyboardButton(text=lre, callback_data=f'lore-to>{lore}?{lre}'))
        menu.row(InlineKeyboardButton(text='◀️', callback_data=f'lore-main'))
        await call.message.edit_text(lore, reply_markup=menu)

    elif call.data.startswith('change-custom-lore'):
        await States.change_custom_lore.set()
        await call.message.edit_text('✍ Write new custom lore:', reply_markup=None)

    elif call.data.startswith('about-lore'):
        lore = call.data.split('>')[1]
        if lore == 'custom':
            with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
                data = json.load(f)
                loredata = data[str(call.from_user.id)]['custom-lore']
            return await call.message.edit_text(f'ℹ️ {lore}:\n{loredata}', reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='◀️', callback_data='lore-to>custom')))
        if '?' in lore:
            loredata = lore_dict[f'{lore.split("?")[0]}'][f'{lore.split("?")[1]}']
            return await call.message.edit_text(f'ℹ️ {lore}:\n{loredata}',
                                                reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='◀️', callback_data=f'lore-to>{lore}')))
        await call.message.edit_text(f'ℹ️ {lore}:\n{lore_dict[lore]}',
                                     reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='◀️', callback_data=f'lore-to>{lore}')))

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
                data[str(call.from_user.id)] = {}
                data[str(call.from_user.id)]['model'] = model
            json.dump(data, f)
        await bot.send_message(call.from_user.id, model)



def setup(dp: Dispatcher):
    dp.register_callback_query_handler(callback, state='*')
