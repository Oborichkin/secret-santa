import logging
import redis

from santa.utils import random_string

r = redis.Redis(host='localhost', port=6379, db=0)
logger = logging.getLogger(__name__)

RETRY = 100


def new_santa(chat_id):
    for i in range(RETRY):
        santa_id = random_string()
        if not r.exists(santa_id):
            r.set(santa_id, chat_id)
            logger.info(f"Added new santa {santa_id} for chat {chat_id}")
            return santa_id
    else:
        raise Exception(f"No unique santas created in {RETRY} times")


def get_participants(santa_id, chat_id):
    assert int(r.get(santa_id)) == chat_id, f"Permission error! Santa was created from {r.get(santa_id)} but accessed from {chat_id}"
    return r.smembers(f"set_{santa_id}")


def enroll(santa_id, chat_id):
    r.sadd(f"set_{santa_id}", chat_id)
    logger.info(f"Added new participant for santa {santa_id}: {chat_id}")
