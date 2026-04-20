from pathlib import Path
import os
import environ
import sys
from django.contrib.messages import constants as messages
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    MYSQL_PORT=(int, 3306),  # cast port to int, default 3306
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
ADMIN_JWT_SECRET = env("ADMIN_JWT_SECRET")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "true") == "true"
SITE_ID = 1
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])


CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
# Application definition
# if not DEBUG:
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # APPS
    "adminuser",
    "accounts",
    "cms",
    "marketing",
    "site_settings",
    # PACKAGES
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    "rest_framework.authtoken",
    "widget_tweaks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "adminuser.middleware.CustomAdminUserMiddleware",
]
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "adminuser.backends.CustomAdminBackend",
]

TIME_ZONE = "Asia/Kolkata"  # or 'UTC', 'America/New_York', etc.
USE_TZ = True

ROOT_URLCONF = "shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "adminuser" / "templates",
        ],
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

WSGI_APPLICATION = "shop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
DOCKER_IP = env("DOCKER_IP", default="host.docker.internal")
if env("SERVER_MODE") != "development":
    INSTANCE_CONNECTION_NAME = env("CLOUD_INSTANCE_NAME")
    print("Using Cloud SQL Database", INSTANCE_CONNECTION_NAME)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("CLOUD_DB_NAME"),
            "USER": env("CLOUD_DB_USER"),
            "PASSWORD": env("CLOUD_DB_PASSWORD"),
            "HOST": f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
            "PORT": "",
            "CONN_MAX_AGE": 3,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "connect_timeout": 3,
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                # Alternatively, you can use:
                # "unix_socket": f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
            },
        }
    }
else:
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': BASE_DIR / "db" / "db.sqlite3",          # fastest — completely in RAM
    #         # Alternative (if you need persistent test db for debugging):
    #         # 'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
    #     }
    # }
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("MYSQL_DATABASE", default="shopper-beats"),
            "USER": env("MYSQL_USER", default="shopper-beats"),
            "PASSWORD": env("MYSQL_PASSWORD", default="cwecifvjki2dif"),
            "PORT": env("MYSQL_PORT", default="3306"),
            "HOST": env("MYSQL_HOST", default="cloudsql-proxy"),
            "CONN_MAX_AGE": 3,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "connect_timeout": 3,
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators


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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "staticfiles"  # or 'static/'

STATIC_DIR_BASE = Path(__file__).resolve().parent.parent
STATICFILES_DIRS = [
    os.path.join(STATIC_DIR_BASE, "static"),
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ACCOUNT_AUTHENTICATION_METHOD = "email"
AUTH_USER_MODEL = "accounts.User"
# AllAuth Email Verification
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # or "optional"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
SITES_FALLBACK = os.getenv("SITES_FALLBACK", "").split(",")
# EMAIL_BACKEND
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # dev
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"  # your SMTP server
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_PORT = 587  # 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True for port 465
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = "2718aditya"
EMAIL_HOST_PASSWORD = env("SENDGRID_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
DEFAULT_FROM_EMAIL = "noreply@shopperbeats.com"
STAKEHOLDER_EMAIL = env("STAKEHOLDER_EMAIL", default="cs@shopperbeats.com.au")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")

ACCOUNT_ADAPTER = "adminuser.custom_adapters.DatabaseEmailAdapter"
# ACCOUNT_ADAPTER = "shop.adapters.MyAccountAdapter"
RECAPTCHA_SECRET = env("RECAPTCHA_SECRET")

ACCESS_TOKEN_TIME_LIMIT = 1  # In days
REFRESH_TOKEN_TIME_LIMIT = 5  # In days
REMEMBER_ME_EXTRA_TIME = 2  # In minutes
ACCESS_TOKEN_LIFETIME = 1000  # minutes
REFRESH_TOKEN_LIFETIME = 7  # days

ACCESS_TOKEN_NAME = "access_token"
REFRESH_TOKEN_NAME = "refresh_token"


MAX_FAILED_LOGIN_ATTEMPTS = 3


BLOCK_DURATION = timedelta(minutes=2)  # In Minutes

ACCOUNT_EMAIL_CONFIRMATION_URL = "resetpassword?key="
# PASSWORD_RESET_CONFIRM_REDIRECT_URL = ""

ADMIN_ACCESS_TOKEN_TIME_LIMIT = 6000  # MINUTES # TODO Decrease it in production
ACCOUNT_EMAIL_CONFIRMATION_MODEL = "accounts.utils.ShortLivedEmailConfirmation"
PRODUCT_SERVICE_URL = env("PRODUCT_SERVICE_URL")
ORDER_SERVICE_URL = env("ORDER_SERVICE_URL")
CART_SERVICE_URL = env("CART_SERVICE_URL")


# ==================================
# Override for testing
# =====================================

if "test" in sys.argv or "testserver" in sys.argv or "pytest" in sys.modules:
    print("Using in-memory SQLite for tests")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",  # fastest — completely in RAM
            # Alternative (if you need persistent test db for debugging):
            # 'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
        }
    }


MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# =====================================
# Celery Configuration
# =====================================
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
