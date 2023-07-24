@echo off


:start
cls

set python_ver=311

pip install openai
pip install aiogram

python main.py
pause
