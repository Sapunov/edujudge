import os
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django.conf import settings

from judge.api.common import translit, random_string


def generate_uniq_username(name, surname):

    name = name.lower()
    surname = surname.lower()

    i = 1
    username = name[:i] + surname

    while User.objects.filter(username=username).exists() and i <= len(name):
        i += 1
        username = name[:i] + surname

    if User.objects.filter(username=username).exists():
        i = 1
        suffix_username = username
        while User.objects.filter(username=suffix_username).exists():
            suffix_username = username + str(i)
            i += 1
        username = suffix_username

    return username


def generate_avatar(initials, username):

    W, H = (400, 400)
    img = Image.new('RGB', (W, H), '#ddd')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'judge/api/content/arial.ttf'), 200)
    w, h = draw.textsize(initials, font=font)
    draw.text(((W - w) / 2, (H - h) / 2), initials, fill="#888", font=font)

    static_dir = os.path.join(settings.BASE_DIR, 'judge', 'ui', 'static') \
        if settings.DEBUG else settings.STATIC_ROOT
    target_dir = os.path.join(static_dir, 'images', 'avatars')

    big_avatar = os.path.join(target_dir, '{0}.png'.format(username))
    small_avatar = os.path.join(target_dir, '{0}_small.png'.format(username))

    img.save(big_avatar)
    img.resize((50, 50)).save(small_avatar)

    return big_avatar


class Command(BaseCommand):

    help = 'Создание студента'

    def add_arguments(self, parser):

        parser.add_argument('name', type=str)
        parser.add_argument('surname', type=str)
        parser.add_argument(
            '--teacher',
            action='store_true',
            help='Создание аккаунта преподавателя',
        )

    def handle(self, *args, **options):

        name = options['name'].lower()
        name_translit = translit(name)
        surname = options['surname'].lower()
        surname_translit = translit(surname)

        username = generate_uniq_username(name_translit, surname_translit)
        password = random_string(8)

        User.objects.create_user(
            username=username, password=password,
            first_name=name.capitalize(),
            last_name=surname.capitalize(),
            is_staff=options['teacher'])

        initials = (name_translit[:1] + surname_translit[:1]).upper()
        path_to_avatar = generate_avatar(initials, username)

        self.stdout.write(
            self.style.SUCCESS(
                'username: {0}, password: {1}, avatar: {2}'.format(
                    username, password, path_to_avatar)))
