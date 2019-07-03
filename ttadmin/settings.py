"""
Local development settings for tildetown-admin.

To run this For Real, you'll want to:

 * set a different SECRET_KEY
 * change the password for the database or delete the password and use ident
 * change DEBUG to False
 * set smtp password
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '!=)!vw!1fi^8*@f78-*go@a@37(obaqq6b1*=zh8vk#ur$ms@t'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'common',
    'users',
    'help',
    'guestbook'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ttadmin',
        'USER': 'ttadmin',
        'PASSWORD': 'ttadmin',
        'HOST': 'localhost',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'

# Not used during local development, but used in staging+live environments
STATIC_ROOT = 'static'

SMTP_PORT=465
SMTP_HOST="smtp.zoho.com"
SMTP_PASSWORD="OVERWRITE THIS"

# Mastodon credentials
MASTO_CLIENT_ID = "OVERWRITE THIS"
MASTO_CLIENT_SECRET = "OVERWRITE THIS"
MASTO_ACCESS_TOKEN = "OVERWRITE THIS"
MASTO_BASE_URL = "https://tiny.tilde.website"

# Twitter credentials
TWITTER_CONSUMER_KEY = "OVERWRITE THIS"
TWITTER_CONSUMER_SECRET = "OVERWRITE THIS"
TWITTER_TOKEN = "OVERWRITE THIS"
TWITTER_TOKEN_SECRET = "OVERWRITE THIS"

