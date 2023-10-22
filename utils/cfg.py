import json

global config, lore_dict, model_dict, buttons, character_limit, Languages
character_limit = 3000

def reload_data():
    global config, lore_dict, model_dict, buttons, Languages

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

    Languages = config['languages']


reload_data()

