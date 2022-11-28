import logging
import redis

from santa.utils import random_string

r = redis.Redis(host="localhost", port=6379, db=0)
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
    if r.exists(santa_id) and int(r.get(santa_id) == chat_id):
        return r.smembers(f"set_{santa_id}")
    raise PermissionError("You are not allowed to see the list of participants for this santa")


def get_creator(santa_id) -> int:
    return int(r.get(santa_id))


# TODO keep list of santa_id's that user is enrolled
def enroll(santa_id, chat_id):
    if not r.exists(santa_id):
        raise Exception("No santa found!")
    r.sadd(f"set_{santa_id}", chat_id)
    logger.info(f"Added new participant for santa {santa_id}: {chat_id}")


def leave(santa_id, chat_id):
    pass  # TODO Allow users to leave
