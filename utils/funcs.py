import json

from utils.imports.imports import *


def timestamp():
    current_time = datetime.now()
    return current_time.timestamp()


async def getlocalized(line: str, lang: str):
    with open('./db/locale.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    try: return data[str(line + '-' + lang[0:2].upper())]
    except:
        try: return data[str(line + '-' + 'EN')]
        except: return 'Failed to translate.'


async def getUser(user_id: str, username = 'None'):
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


def getkey(type: str = 'gpt-3.5') -> str:

    with open('./openai.keys.json', 'r') as f:
        keys = json.load(f)

        return random.choice(keys[type])


async def getUserStats():
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


async def getLore(lore: str):
    with open('./db/lore-list.json', 'r', encoding='UTF-8') as f:
        lore_dict = json.load(f)
    try:
        if '?' in lore:
            return lore_dict[lore.split('?')[0]][lore.split('?')[1]]
        else: return lore_dict[lore]
    except: return ' '
