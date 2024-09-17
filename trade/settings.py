"""
Django settings for trade project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/

pip install --upgrade pip && pip install -r requirements.txt
gunicorn --workers=1 --threads=3 trade.wsgi:application

"""
import os
import dj_database_url
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-xt)&*v#+#^4-wimy)oo1v5jn4zmu94xqbuh^ac$)r*%=834_hf"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://algo-nse.onrender.com,https://localhost:8000,https://127.0.0.1:8000,https://pratikmahobiya-fuzzy-space-giggle-6474w56pgxxf4w9r-8000.preview.app.github.dev').split(',')

BED_URL_DOMAIN = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://algo-nse.onrender.com')
SOCKET_STREAM_URL_DOMAIN = 'https://algo-nse-socket-service.onrender.com'

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "admin_extra_buttons",
    "import_export",

    "system_conf",
    "stock",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "trade.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "trade.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': dj_database_url.parse("postgresql://crypto_bros_424l_user:OkfUQXu4bsaEeijVxBqzmdpdaUEiSQ3k@dpg-cr65avjv2p9s73amqva0-a/crypto_bros_424l", conn_max_age=0),
# } if os.getenv('SERVER_DB', False) else {
#     'default': dj_database_url.parse("postgresql://crypto_bros_424l_user:OkfUQXu4bsaEeijVxBqzmdpdaUEiSQ3k@dpg-cr65avjv2p9s73amqva0-a.virginia-postgres.render.com/crypto_bros_424l", conn_max_age=0),
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True

USE_L10N = False

DATETIME_FORMAT = 'N j, Y, g:i:s a'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Broker Detail
BROKER_PIN = 4567
BROKER_USER_ID = 'P567723'
BROKER_API_KEY = 'ExEEsqVb'
BROKER_TOTP_KEY = 'VF4PNLIJZSO5CK7AILPR2ETP2M'


# Global Variable
global broker_connection

import pyotp
from SmartApi import SmartConnect
connection = SmartConnect(api_key=BROKER_API_KEY)
connection.generateSession(BROKER_USER_ID, BROKER_PIN, totp=pyotp.TOTP(BROKER_TOTP_KEY).now())

broker_connection = connection

