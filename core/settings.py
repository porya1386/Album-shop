"""
Django settings for core project (Jahan art shop).

Everything that changes between your PC and the server (Hamravesh) is read with
python-decouple: first from environment variables, then from the .env file.
"""
from pathlib import Path

from decouple import Csv, config, RepositoryEnv, Config
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env"

if env_file.exists():
    env_config = Config(RepositoryEnv(str(env_file)))
else:
    env_config = Config({})
# --------------------------------------------------
# Core
# --------------------------------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

# your domain(s) on the server, e.g.  jahan.example.ir,www.jahan.example.ir
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,192.168.1.5",
    cast=Csv(),
)
# ALLOWED_HOSTS = [
#     "localhost",
#     "127.0.0.1",
# ]
# full origins WITH https://  (needed for login and forms on the server)
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# --------------------------------------------------
# Application definition
# --------------------------------------------------
INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # My apps
    'website',
    'shop',
    'reviews',
    'blogs',
    # installed apps
    'drf_yasg',
    'rest_framework',
    'widget_tweaks',
    "django_recaptcha",
    # login with Google / GitHub
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # serves /static/ on the server (no nginx)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # django-allauth
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# --------------------------------------------------
# Database
#   POSTGRES_DB set  -> PostgreSQL (Docker / Hamravesh)
#   POSTGRES_DB empty -> sqlite file (quick local run without Docker)
# --------------------------------------------------
POSTGRES_DB = config("POSTGRES_DB", default="")

if POSTGRES_DB:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB,
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD"),
            "HOST": config("POSTGRES_HOST", default="127.0.0.1"),
            "PORT": config("POSTGRES_PORT", default="5432"),
            "CONN_MAX_AGE": 60,
            # fail fast (5 s) with a clear error if Postgres is not running,
            # instead of waiting forever
            "OPTIONS": {"connect_timeout": 5},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --------------------------------------------------
# Google reCAPTCHA
# --------------------------------------------------
RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_DOMAIN = config("RECAPTCHA_DOMAIN", default="www.recaptcha.net")

# --------------------------------------------------
# Cache / Rate limiting
#   REDIS_URL set   -> Redis (shared by all gunicorn workers: needed for django-ratelimit)
#   REDIS_URL empty -> memory cache (fine for local runserver only)
# --------------------------------------------------
REDIS_URL = config("REDIS_URL", default="")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        },
        "ratelimit": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "KEY_PREFIX": "album-shop-ratelimit",
        },
    }
else:
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "ratelimit": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ratelimit",
        },
    }

RATELIMIT_USE_CACHE = "ratelimit"

# --------------------------------------------------
# Password validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# Internationalization
# --------------------------------------------------
USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("fa", _("فارسی")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

USE_TZ = True

# --------------------------------------------------
# Static files (CSS, JavaScript, Images) - served by WhiteNoise
# --------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / 'static']
# collectstatic puts everything here
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------
# Media (uploads: images and videos)
#   S3_BUCKET set   -> MinIO / S3 (best for videos)
#   S3_BUCKET empty -> files in the media/ folder
# --------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # no "Manifest" here: it crashes collectstatic if a CSS file points to a missing image
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

S3_BUCKET = config("S3_BUCKET", default="")
if S3_BUCKET:
    INSTALLED_APPS += ["storages"]
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}
    AWS_STORAGE_BUCKET_NAME = S3_BUCKET
    AWS_S3_ENDPOINT_URL = config("S3_ENDPOINT")
    AWS_ACCESS_KEY_ID = config("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = config("S3_SECRET_KEY")
    AWS_S3_ADDRESSING_STYLE = "path"
    AWS_QUERYSTRING_AUTH = False                 # public files, plain links
    AWS_S3_FILE_OVERWRITE = False
    # the address the BROWSER uses
    S3_PUBLIC_URL = config("S3_PUBLIC_URL", default="")
    if S3_PUBLIC_URL:
        MEDIA_URL = S3_PUBLIC_URL.rstrip("/") + "/"

# --------------------------------------------------
# Upload limits (Django has no file-size limit; the 100 MB video limit is in shop/models.py)
# --------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024    # form text only, not files
# bigger files are streamed to a temp file
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# --------------------------------------------------
# Behind Hamravesh's HTTPS proxy (only when DEBUG is False)
# --------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config(
        "SECURE_SSL_REDIRECT", default=False, cast=bool)
    # raise it AFTER https works
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)

# --------------------------------------------------
# Login with Google / GitHub (django-allauth)
# --------------------------------------------------
AUTHENTICATION_BACKENDS = [
    # username + password (as before)
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",    # Google / GitHub
]

# Keys come from .env (PC) or the Hamravesh panel (server). Empty = the button just fails.
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID", default=""),
            "secret": config("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
    "github": {
        "APP": {
            "client_id": config("GITHUB_CLIENT_ID", default=""),
            "secret": config("GITHUB_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": ["user:email"],          # to get the verified email
    },
}

# new user: account is created, no extra form
SOCIALACCOUNT_AUTO_SIGNUP = True
# login only with POST (the buttons are POST forms)
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
SOCIALACCOUNT_STORE_TOKENS = False
# we do not send verification mails (yet)
ACCOUNT_EMAIL_VERIFICATION = "none"
# used to build the callback address
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if DEBUG else "https"
# behind Hamravesh's proxy
ALLAUTH_TRUSTED_PROXY_COUNT = 0 if DEBUG else 1

# --------------------------------------------------
# Email - Mailerino SMTP
# --------------------------------------------------

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": env_config("EMAIL_HOST", default=""),
            "port": env_config("EMAIL_PORT", default=587, cast=int),
            "use_tls": env_config("EMAIL_USE_TLS", default=True, cast=bool),
            "use_ssl": env_config("EMAIL_USE_SSL", default=False, cast=bool),
            "username": env_config("EMAIL_HOST_USER", default=""),
            "password": env_config("EMAIL_HOST_PASSWORD", default=""),
        },
    },
}

DEFAULT_FROM_EMAIL = env_config(
    "DEFAULT_FROM_EMAIL",
    default="webmaster@localhost",
)
# --------------------------------------------------
# Login redirect
# --------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "products"
LOGOUT_REDIRECT_URL = "accounts:login"

# --------------------------------------------------
# Captcha
# --------------------------------------------------
SILENCED_SYSTEM_CHECKS = [
    "django_recaptcha.recaptcha_test_key_error"
]

AUTH_USER_MODEL = "accounts.CustomUser"
