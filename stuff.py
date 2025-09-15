import datetime
import json
import os
import random
import sqlite3
from discord.ext import tasks
from profanityfilter import ProfanityFilter
from uwuipy import Uwuipy
import logging
import logging.handlers
import dotenv

import data

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    filename="logs/stuff.log",
    encoding='utf-8',
    maxBytes=32*1024*1024,
    backupCount=128,
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

handler.setFormatter(formatter)
logger.addHandler(handler)

def get_bot_token():
    return os.getenv('TOKEN')

def set_if_not_exists(config: dict, key, value):
    try:
        for k in config.keys():
            logger.debug(f"ArrayKey: {k}")
            if k == key:
                logger.debug(f"Found matching: {k}")
                return
        config[key] = value
    except Exception as e:
        logger.error(f"Exception occured; {e} 3:")
        return False
    return True

def cset(config: dict, key, value):
    try: config[key] = value
    except Exception as e:
        logger.error(f"Exception occured while trying to set config {key} to {value}: {e} 3:") 
        return False
    return True

async def isInt(s):
    try:
        logger.debug(f"Is {s} integer?")
        int(s,10)
    except ValueError:
        logger.debug(f"Nopeee!!11!@ 3:<")
        return False
    else:
        logger.debug("Yes sir! :3")
        return True

async def change_toggles(config:dict, key: str):
    if not key:
        logger.warning("Not provided 3:")
        print("Not provided 3:")
    
    
    for k in config.keys():
        print(k)
        logger.debug(f"Searching {k} is matching with name {key}...")
        if k == key:
            logger.debug(f"Matching found: {k} {key} :3")
            config[k] = not config[k]
            print(f"Changed {k} to {config[k]} :3")
            return
    
    print(f"{key} not found from config 3:")
    logger.debug(f"{key} not found 3:")
    return

def censor(pf: ProfanityFilter,text: str):
    logger.debug(f"Process {text}")
    return pf.append_words(text)

def muffle(text: str):
    result = []
    for char in text:
        logger.debug(f"Char: {char}")
        target = char
        if target.isalpha():
            logger.debug(f"The char is Alphabet")
            if target not in 'whpmnuf':
                logger.debug(f"Target will be muffled.")
                target = "m"
        
        logger.debug(f"Appending...")
        result.append(target)

    logger.debug(f"Result: {"".join(result)} ({text})")
    return "".join(result) + f" ({text})"

def uwuify(uwu,text: str):
    logger.debug(f"Text {text} will be uwuified.")
    return uwu.uwuify(text)

def save(config: dict):
    logger.debug(f"Saving data to settings.json")
    with open("settings.json","w",encoding="utf-8") as f:
        json.dump(config,f,ensure_ascii=False,indent=4)

def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        logger.debug("Folder not found. makedirectory")
        os.makedirs(path,exist_ok=True)

def format_extra(input:str):
    logger.debug(f"Format extra: {input}")
    if not input:
        return ""
    
    result = ""
    i = 0
    while i < len(input):
        logger.debug(f"Index: {i}, Char: {input[i]}")
        char = input[i]
        if char == '+':
            logger.debug("Char is '+'")
            if i > 0:
                plus = 0
                j = i
                while j < len(input) and input[j] == '+':
                    plus += 1
                    j += 1
                
                rep = input[i-1]
                repeats = random.randint(1,plus)
                result += rep*repeats
                i=j
            else:
                i += 1
        else:
            result += char
            i += 1
    return result

def setup_database(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id TEXT PRIMARY KEY,
            pox_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def three_commas(x):
    b,a = divmod(len(x), 3)
    return ",".join(([x[:a]] if a else []) + [x[a+3*i:a+3*i+3] for i in range(b)])

def is_weekday(time: datetime.datetime):
    weekday = time.weekday()

    if weekday >= 0 and weekday <= 4:
        return True
    else:
        return False

def is_specificweek(time: datetime.datetime,week:int):
    weekday = time.weekday()

    if weekday == week:
        return True
    else:
        return False

def is_within_hour(time: datetime.datetime,fromhour:int,tohour:int):
    hour = time.hour

    if hour >= fromhour and hour < tohour:
        return True
    else:
        return False

def is_sleeping(time: datetime.datetime,fromhour:int,tohour:int):
    hour = time.hour

    if hour >= fromhour or hour < tohour:
        return True
    else:
        return False

def check_map(score: float,max:int):
    map = data.possible_map
    map_len = len(map)
    size = max // map_len

    scores = {}
    for i, name in enumerate(map):
        start = i * size
        end = start + size
        if i == map_len-1:
            end = max+1
        scores[range(start,end)] = name
    for sr,txt in scores.items():
        if score in sr:
            return map[txt]

def get_formatted_from_seconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minute = seconds // 60
    seconds %= 60
    return f"{hour} hours {minute} minutes {seconds} seconds"