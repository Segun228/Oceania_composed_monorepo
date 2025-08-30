import os
from dotenv import load_dotenv
from pathlib import Path
import dj_database_url  # type: ignore

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
debug = os.getenv("DEBUG")
database = os.getenv("DATABASE_URL")

BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'authentication.User'
CORS_ALLOW_ALL_ORIGINS = True
SECRET_KEY = secret_key


DEBUG = debug


ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "authentication",
    "photos",
    "reports",
    'drf_spectacular',
    'drf_spectacular_sidecar',
    "rest_framework",
    "corsheaders",
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

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'backend.authentication.TelegramAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


DATABASES = {
    'default': dj_database_url.config(
        default=database
    )
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

SPECTACULAR_SETTINGS = {
    'TITLE': 'My Project API',
    'DESCRIPTION': 'API документация моего проекта',
    'VERSION': '1.0.0',
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'backend/staticfiles')
STATICFILES_DIRS = []



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
