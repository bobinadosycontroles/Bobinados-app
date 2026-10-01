from .base import *  # noqa: F403, F401

DEBUG = False
ALLOWED_HOSTS = ['67.205.133.106', 'app.bobinados.com']
SITE_URL = 'http://app.bobinados.com/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bobinados',
        'USER': 'bobinados',
        'PASSWORD': 'Bobinados2026!',
        'HOST': '67.205.133.106',
        'PORT': '5432',
    }
}


MEDIA_ROOT = '/media/'  # Docker volume
STATIC_ROOT = "/public/"  # Docker volume
