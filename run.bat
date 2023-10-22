@echo off


:start
cls

set python_ver=311

pip install openai
pip install aiogram=2.22.2
pip install requests
pip install python-dotenv

python main.py
pause
