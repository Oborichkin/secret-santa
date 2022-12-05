from typing import List
import logging
import redis

from santa.utils import random_string

r = redis.Redis(host="redis", port=6379, db=0)
logger = logging.getLogger(__name__)

RETRY = 100


def add_user_info(chat_id: int, info: str):
    r.set(f"user_{chat_id}", info)


def get_user_info(chat_id: int) -> str:
    if info := r.get(f"user_{chat_id}"):
        return info.decode("utf-8")


def remove_user_info(chat_id: int):
    r.delete(f"user_{chat_id}")


def new_santa(chat_id):
    for i in range(RETRY):
        santa_id = random_string()
        if not r.exists(santa_id):
            r.set(santa_id, chat_id)
            logger.info(f"Added new santa {santa_id} for chat {chat_id}")
            return santa_id
    else:
        raise Exception(f"No unique santas created in {RETRY} times")


def get_participants(santa_id, chat_id) -> List[int]:
    if r.exists(santa_id) and int(r.get(santa_id)) == chat_id:
        return [int(member) for member in r.smembers(f"set_{santa_id}")]
    logger.error(f"{int(r.get(santa_id))} == {chat_id}")
    logger.error(r.exists(santa_id) and int(r.get(santa_id) == chat_id))
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
