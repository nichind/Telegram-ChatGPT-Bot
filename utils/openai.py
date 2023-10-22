from utils.funcs import getkey
import requests


async def _generate_response_async(message_log: list, model: str):
    while 1:
        try:
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {'Authorization': f"Bearer {getkey()}"}
            data = {'model': 'gpt-3.5-turbo', 'messages': message_log}
            response = requests.post(url, headers=headers, json=data).json()
            print(response)
            res = response['choices'][0]['message']['content']
            #res = res.encode()
            return res
        except Exception as e: print(e)