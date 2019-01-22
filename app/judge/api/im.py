import redis
import pickle
import json
from hashlib import sha1
from datetime import datetime

from django.conf import settings


connection = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


class Messages:

    def __init__(self, messages):

        self.count_messages = len(messages)
        self.messages = messages


def data_hash(bytes_string):

    return sha1(bytes_string).hexdigest()


def unpack_messages(messages):

    for i in range(len(messages)):
        messages[i] = pickle.loads(messages[i])
        messages[i]['payload'] = json.dumps(messages[i]['payload'])


def pack_message(message):

    return pickle.dumps(message)


def get_user_messages(user_id):

    keys = connection.keys('{0}:{1}*'.format(settings.IM_REDIS_PREFIX, user_id))

    if keys:
        messages = connection.mget(keys)
        connection.delete(*keys)

        unpack_messages(messages)

        return Messages(messages)


def send_message(user_id, msg_type, message, alert_msg=None):

    if isinstance(user_id, list):
        for uid in user_id:
            send_message(uid, msg_type, message, alert_msg)
    else:
        data = pack_message({
            'msg_type': msg_type,
            'alert_msg': alert_msg,
            'payload': message
        })

        key = '{0}:{1}:{2}:{3}'.format(
            settings.IM_REDIS_PREFIX,
            user_id,
            data_hash(data),
            datetime.now()
            )

        connection.set(key, data, ex=settings.IM_REDIS_EX)
