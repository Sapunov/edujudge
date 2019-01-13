import logging
import pymorphy2
import random
import string

from django.contrib.auth.models import User


def get_logger(name):

    return logging.getLogger(name)


def word_gent(word):

    morph = pymorphy2.MorphAnalyzer()

    objects = morph.parse(word)

    if len(objects) > 1:
        objects.sort(key=lambda it: len(it.normal_form), reverse=True)

    objectt = objects[0]

    inflected_result = objectt.inflect({'gent'})
    if inflected_result:
        inflected = inflected_result.word

        if word[0].isupper():
            inflected = inflected.capitalize()

        return inflected
    return word


def get_staff_ids(exclude=None):

    users = User.objects.filter(is_staff=True)
    ids = set()

    if len(users) > 0:
        ids.update([it.id for it in users])

    if exclude is not None:
        ids = ids - set(exclude)

    return list(ids)


def translit(string):

    dic = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ь': '',
        'ы': 'y', 'ъ': '', 'э': 'e', 'ю': 'ju', 'я': 'ja', 'a': 'а', 'b': 'б',
        'c': 'ц', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х', 'i': 'и',
        'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
        'q': 'q', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'w',
        'x': 'x', 'y': 'ы', 'z': 'з'
    }

    result = ''

    for letter in string:
        result += dic.get(letter, letter)

    return result


def random_string(length):

    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
