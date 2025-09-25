import json
from logging import getLogger, DEBUG, INFO, Formatter
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
logger = getLogger('discord')
logger.setLevel(DEBUG)

with open('conf/logging.json', 'r') as f:
    log_conf = json.load(f)

dictConfig(log_conf)

"""getLogger('discord.http').setLevel(INFO)

handler = RotatingFileHandler(
    filename="logs/discord.log",
    encoding='utf-8',
    maxBytes=32*1024*1024,
    backupCount=128,
)

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

handler.setFormatter(formatter)
logger.addHandler(handler)"""