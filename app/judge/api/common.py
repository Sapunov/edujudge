import pymorphy2

from django.contrib.auth.models import User


def word_gent(word):

    morph = pymorphy2.MorphAnalyzer()

    objects = morph.parse(word)

    if len(objects) > 1:
        objects.sort(key=lambda it: len(it.normal_form), reverse=True)

    objectt = objects[0]

    inflected = objectt.inflect({'gent'}).word

    if word[0].isupper():
        inflected = inflected.capitalize()

    return inflected


def get_staff_ids(exclude=None):

    users = User.objects.filter(is_staff=True)
    ids = set()

    if len(users) > 0:
        ids.update([it.id for it in users])

    if exclude is not None:
        ids = ids - set(exclude)

    return list(ids)
