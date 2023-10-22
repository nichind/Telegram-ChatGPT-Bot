import asyncio
import types
import aiogram.utils.executor
from utils.imports.imports import *


async def send(message: types.Message, state: FSMContext):
    await message.delete()
    if message.from_user.id == config['admin-id']:
        await AdminStates.send_message.set()
        msg = await bot.send_message(message.from_user.id, '📝 Write message for mailing.')
        await state.update_data(message=msg)


async def send_message(message: types.Message, state: FSMContext):
    await (await state.get_data())['message'].delete()
    await state.finish()
    msg = await message.copy_to(message.from_user.id)
    await message.delete()
    markup = InlineKeyboardMarkup(row_width=2).row(InlineKeyboardButton(text='✅', callback_data=f'send-yes?{msg.message_id}'), InlineKeyboardButton(text='⛔', callback_data=f'send-no?{msg.message_id}'))
    markup.row(InlineKeyboardButton(text='🚫 Start button', callback_data=f'send-start?{msg.message_id}'))
    markup.row(InlineKeyboardButton(text='Make link button', callback_data=f'send-link?{msg.message_id}'))
    await state.update_data(message=msg)
    await state.update_data(start=False)
    await state.update_data(link=False)
    await bot.send_message(message.from_user.id, 'Are you sure you want to start mailing this message?', reply_to_message_id=msg.message_id, reply_markup=markup)


async def send_link_button(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_state(with_data=False)
    await (await state.get_data())['temp'].delete()
    if len(message.text.split(';')) != 2:
        return
    else:
        await state.update_data(link_label=message.text.split(';')[0])
        await state.update_data(link_url=message.text.split(';')[1])
        await state.update_data(link=True)
        msg = (await state.get_data())['message']
        markup = InlineKeyboardMarkup(row_width=2).row(
            InlineKeyboardButton(text='✅', callback_data=f'send-yes?{msg.message_id}'),
            InlineKeyboardButton(text='⛔', callback_data=f'send-no?{msg.message_id}'))
        markup.row(
            InlineKeyboardButton(text=f'{"🚫" if (await state.get_data())["start"] is False else "✅"} Start button',
                                 callback_data=f'send-start?{msg.message_id}'))
        markup.row(
            InlineKeyboardButton(text='Make link button', callback_data=f'send-link?{msg.message_id}') if
            (await state.get_data())['link'] is False else
            InlineKeyboardButton(text=(await state.get_data())['link_label'],
                                 url=(await state.get_data())['link_url']))
        await (await state.get_data())['menu_msg'].edit_reply_markup(markup)


async def send_callback(call: CallbackQuery, state: FSMContext):
    await state.update_data(menu_msg=call.message)
    if call.data.split('-')[1].startswith('no'):
        await call.message.delete()
        await (await state.get_data())['message'].delete()
        await state.finish()
    elif call.data.split('-')[1].startswith('start'):
        await state.update_data(start=True if (await state.get_data())['start'] is False else False)
        markup = InlineKeyboardMarkup(row_width=2).row(
            InlineKeyboardButton(text='✅', callback_data=f'send-yes?{call.data.split("?")[1]}'),
            InlineKeyboardButton(text='⛔', callback_data=f'send-no?{call.data.split("?")[1]}'))
        markup.row(InlineKeyboardButton(text=f'{"🚫" if (await state.get_data())["start"] is False else "✅"} Start button', callback_data=f'send-start?{call.data.split("?")[1]}'))
        markup.row(InlineKeyboardButton(text='Make link button', callback_data=f'send-link?{call.data.split("?")[1]}') if (await state.get_data())['link'] is False else
                   InlineKeyboardButton(text=(await state.get_data())['link_label'], url=(await state.get_data())['link_url']))
        await call.message.edit_reply_markup(reply_markup=markup)
    elif call.data.split('-')[1].startswith('link'):
        msg = await call.message.reply('Enter button label & url like this: `label;url`', parse_mode='markdownv2')
        await AdminStates.send_message_link.set()
        await state.update_data(temp=msg)
    else:
        with open('./db/user-settings.json', 'r', encoding='UTF-8') as f:
            data = json.load(f)
            index, count, errors = 0, 1, {'Chat not found': 0, 'Blocked': 0, 'Not defined': 0}
            stats = await call.message.edit_text(f'0 / {len(data)}', reply_markup=None)
            markup = InlineKeyboardMarkup(row_width=1)
            if (await state.get_data())['start'] is True: markup.row(InlineKeyboardButton(text='🤖', callback_data='start'))
            if (await state.get_data())['link'] is True: markup.row(InlineKeyboardButton(text=(await state.get_data())['link_label'], url=(await state.get_data())['link_url']))
            for user in data.keys():
                try:
                    await bot.copy_message(from_chat_id=call.from_user.id, message_id=call.data.split('?')[1], chat_id=int(user), reply_markup=markup)
                    index+=1
                    await asyncio.sleep(0.13)
                except aiogram.exceptions.ChatNotFound:
                    errors['Chat not found'] += 1
                except aiogram.exceptions.BotBlocked:
                    errors['Blocked'] += 1
                except Exception as e:
                    errors['Not defined'] += 1
                try: await bot.edit_message_text(message_id=stats['message_id'], chat_id=call.from_user.id, text=f'{index} / {len(data)} try: {count}')
                except: pass
                count += 1
            await call.message.edit_text(text=f'🏁 {index} / {len(data)} \n\n⛔ {errors["Chat not found"] + errors["Blocked"] + errors["Not defined"]}\nChat Not Found: {errors["Chat not found"]}\nBlocked bot: {errors["Blocked"]}\nOther: {errors["Not defined"]}')


async def reload(message: types.Message, state: FSMContext):
    if message.from_user.id ==  config['admin-id']:
        reload_data()
        await message.delete()
        msg = await bot.send_message(message.from_user.id, '✅ Reloaded!')
        await asyncio.sleep(5)
        await msg.delete()


def setup(dp: Dispatcher):
    dp.register_message_handler(send, content_types=['text'], state=None, commands=['send'])
    dp.register_message_handler(send_message, state=AdminStates.send_message, content_types=aiogram.types.ContentType.all())
    dp.register_message_handler(send_link_button, state=AdminStates.send_message_link)
    dp.register_callback_query_handler(send_callback,lambda call: call.data.startswith('send-'))
    dp.register_message_handler(reload, state='*', commands=['reload'])