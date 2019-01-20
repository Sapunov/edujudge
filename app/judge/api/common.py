import logging
import pymorphy2
import random
import string

from django.contrib.auth.models import User


def get_logger(name):

    return logging.getLogger(name)


def word_gent(word, gender=None):

    morph = pymorphy2.MorphAnalyzer()

    objects = morph.parse(word)

    if not len(objects):
        return word, gender

    if len(objects) > 1:
        objects.sort(key=lambda it: len(it.normal_form), reverse=True)

    if gender is not None:
        objects = list(filter(lambda it: it.tag.gender == gender, objects))

    objectt = objects[0]
    gender = objectt.tag.gender

    inflected_result = objectt.inflect({'gent'})
    if inflected_result:
        inflected = inflected_result.word

        if word[0].isupper():
            inflected = inflected.capitalize()

        return inflected, gender
    return word, gender


def inflect_name(name, surname):

    name_inflected, gender = word_gent(name)
    surname_inflected, _ = word_gent(surname, gender)

    return '{} {}'.format(name_inflected, surname_inflected)


def get_staff_ids(exclude=None):

    assert exclude is None or isinstance(exclude, list), 'Exclude must be list'

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


def count_data_types(list_of_items):

    assert isinstance(list_of_items, (list, tuple)), \
        'list_of_items must be of type list or tuple'

    count_map = {}

    for item in list_of_items:
        type_name = type(item).__name__
        if type_name in count_map:
            count_map[type_name] += 1
        else:
            count_map[type_name] = 1

    return count_map


def list_to_dict(objs_list, key):

    result = {}

    for obj in objs_list:
        if key not in obj:
            raise ValueError('Key not in obj')
        if obj[key] in result:
            raise ValueError('Duplicate key: {}'.format(obj[key]))
        result[obj[key]] = obj

    return result
