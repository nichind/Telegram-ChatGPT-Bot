import asyncio
import json
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from aiogram.dispatcher.filters.builtin import CommandStart
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
import requests
import random
from utils import cfg
from utils.cfg import *
from utils.bot import bot
from utils.states.states import *
from utils.funcs import *
import utils.openai as chatgpt
import threading
from utils.formatting import formatter
from dotenv import load_dotenv
