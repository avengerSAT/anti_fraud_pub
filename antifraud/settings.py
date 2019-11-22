import os

from dotenv import load_dotenv
from pathlib import Path
env_path = Path('./antifraud/') / '.env'
load_dotenv(dotenv_path=env_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



SECRET_KEY = os.getenv('SCRT_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']




INSTALLED_APPS = [
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'django_filters',


    'channels',
    'channels_redis',


    'leaflet',
    'fraud_inspector',
    'menu',
    'check',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'antifraud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
 	'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'antifraud.wsgi.application'



# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

#DATABASES = {
#   'default': {
#       'ENGINE': 'django.db.backends.sqlite3',
#       'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
#   }
#}

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': os.getenv('name'),
         'USER': os.getenv('user'),
         'PASSWORD': os.getenv('password'),
         'HOST': os.getenv('host'),
         'PORT': os.getenv('port')
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




LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow' 

USE_I18N = True

USE_L10N = True

USE_TZ = True


ASGI_APPLICATION='antifraud.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('0.0.0.0', 6379),],
        },
    },
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'django_plotly_dash.finders.DashAssetFinder',
    'django_plotly_dash.finders.DashComponentFinder',
    'django_plotly_dash.finders.DashAppDirectoryFinder',
]

PLOTLY_COMPONENTS = [
    'dash_core_components',
    'dash_html_components',
    'dash_renderer',
    'dpd_components',
]

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/menu/'

MEDIA_URL = '/media/'

MEDIA_DIR = os.path.join(BASE_DIR, 'media')

PLOTLY_DASH = {
    "ws_route" : "ws/channel",

    "insert_demo_migrations" : True,  # Insert model instances used by the demo

    "http_poke_enabled" : True, # Flag controlling availability of direct-to-messaging http endpoint

    "view_decorator" : None, # Specify a function to be used to wrap each of the dpd view functions

    "cache_arguments" : True, # True for cache, False for session-based argument propagation

    #"serve_locally" : True, # True to serve assets locally, False to use their unadulterated urls (eg a CDN)

    "stateless_loader" : "demo.scaffold.stateless_app_loader",
    }