import json
from logging import basicConfig, getLogger, DEBUG, INFO, Formatter, root
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from rich.logging import RichHandler

logger = getLogger('bot')
#logger.setLevel(DEBUG)

with open('conf/logging.json', 'r') as f:
    log_conf = json.load(f)

dictConfig(log_conf)

logger.addHandler(RichHandler(rich_tracebacks=True))
getLogger("discord").addHandler(RichHandler(level="INFO",rich_tracebacks=True))
getLogger("stuff").addHandler(RichHandler(level="DEBUG",rich_tracebacks=True))
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