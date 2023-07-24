@echo off


:start
cls

set python_ver=311

python ./get-pip.py

cd \
cd \python%python_ver%\Scripts\
pip install openai
pip install aiogram

pause
exit
