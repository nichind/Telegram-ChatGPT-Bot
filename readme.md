# Telegram ChatGPT Bot
**My ChatGPT Free bot - https://t.me/chimeragptrobot**

if you have any questions or(and) suggestions feel free to join my discord server https://discord.gg/GnDz3RYq9y

# Installation
1. Install Python 3.11 from https://www.python.org/downloads

2. Run```python3.11 -m pip install -r requirements.txt```

3. Create `.env` file in bot directory

4. Paste your bot token in `.env`
```dotenv filename=".env"
token=YourBotToken
```

5. Paste your **OpenAI** api token in `openai.keys.json`
```json
{
  "gpt-3.5": [
        "Your token 1",
        "Your token 2 (Optional)"
    ],
  "gpt-4": [
        "You gpt-4 token 1 (Optional)"
  ]
}
```

6. Paste your telegram id in `config.json`
```json
{
    "admin-id": 1234567890
}
```

# Commands

| Command | Explanation            |
|---------|------------------------|
| /reload | Reload **config.json** |
| /send   | Mailing bot users      |
| /stats  | Bot user count         |

<img src="https://komarev.com/ghpvc/?username=nichind-telegramchatgpt&color=brightgreen" alt="watching_count" />