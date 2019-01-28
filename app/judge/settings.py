import os

NAME = 'judge'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join('/var/lib/', NAME, 'data')
VERSION = '0.11.0'

SECRET_KEY = 'somestrongdjangokey'

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'judge.ui',
    'judge.api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'judge.api.middleware.LastActivityMiddleware',
]


ROOT_URLCONF = 'judge.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'judge.wsgi.application'


if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
        }
    }

    REDIS_HOST = 'localhost'
else:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'postgres',
            'USER':     'postgres',
            'HOST':     'postgres',
            'PORT':     '5432',
        },
    }

    REDIS_HOST = 'redis'


REDIS_PORT = 6379
REDIS_DB = 0


RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': REDIS_DB,
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

LOGIN_URL = '/auth/login'

SOURCE_DIR = os.path.join(DATA_DIR, 'user_sources')

TEST_GENERATORS_DIR = os.path.join(DATA_DIR, 'test_generators')

TEST_CHECKERS_DIR = os.path.join(DATA_DIR, 'test_checkers')

TEST_ERRORS = [
    'Полное решение',
    'Ошибка компиляции программы',
    'Неправильный ответ',
    'Превышено ограничение по времени'
]

LOGS_DIR = os.path.join(DATA_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(filename)s:'
                      '%(funcName)s:%(lineno)s '
                      '%(levelname)s: %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(message)s'
        },
    },
    'handlers': {
        'main': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'main.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'main': {
            'handlers': ['main'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}

STATIC_ROOT = os.path.join(DATA_DIR, 'static')

IM_REDIS_PREFIX = 'judge:im'

# How many seconds IM message stores in redis
IM_REDIS_EX = 300  # 5 minutes

TEST_INPUT_MAX_LEN = 500

UI_DATETIME_FORMAT = '%d.%m.%Y @ %H:%M:%S'
