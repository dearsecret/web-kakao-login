import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

if (BASE_DIR / ".env.dev").exists():
    env_file = BASE_DIR / ".env.dev"
    environ.Env.read_env(str(env_file))
    
    
DOMAIN_NAME = os.getenv("DOMAIN_NAME")
SUBDOMAIN = os.getenv("SUBDOMAIN")
BACKEND_DOMAIN =f"{SUBDOMAIN}.{DOMAIN_NAME}"
    

DEBUG = env.bool("DEBUG", default=True)
# FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "google_service_account.json") if DEBUG else env("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", default="/app/google_service_account.json")
redis_host = 'redis'
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
CORS_ALLOWED_ORIGINS = [
        f"https://{DOMAIN_NAME}",
        f"https://www.{DOMAIN_NAME}",
        f"https://{BACKEND_DOMAIN}"
    ]
    

if DEBUG:
    # GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', '/usr/local/Cellar/gdal/3.11.0_1/lib/libgdal.dylib')
    # print("daphne config.asgi:application --port 8000 \n celery -A config worker --loglevel=info \n poetry run celery -A config beat --loglevel=info")
    import socket
    from django.core.management.commands.runserver import Command as runserver
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try : 
        s.connect(("8.8.8.8", 80))
        ipaddr= s.getsockname()[0]
        s.close()
    except : 
        ipaddr= s.getsockname()[0]
        print("=============the wifi connection wasn't good=============")
    runserver.default_port = '8000'
    runserver.default_addr = ipaddr
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", "0.0.0.0",ipaddr]
    CORS_ALLOWED_ORIGINS = [
            "http://127.0.0.1",
            "http://127.0.0.1:8000",
        ]
    redis_host = 'localhost'


    
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

CELERY_BROKER_URL = f'redis://{redis_host}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{redis_host}:6379/0'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
REDIS_URL = f'redis://{redis_host}:6379/1'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_ENABLE_UTC = False

CLIENT_ID = os.getenv('KAKAO_API_KEY')
CLIENT_SECRET = os.getenv('KAKAO_SECRET')


SECRET_KEY = env("SECRET_KEY")
# GOOGLE_PLAY_PACKAGE_NAME = "com.yourcompany.yourapp"

# AWS_ACCESS_KEY = env("AWS_ACCESS_KEY")
# AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET = env("AWS_STORAGE_BUCKET")
# AWS_REGION = env("AWS_REGION")
# AWS_CUSTOM_DOMAIN = "%s.s3.%s.amazonaws.com"%(AWS_STORAGE_BUCKET, AWS_REGION)

# 문자메시지 서비스 환경변수
# SMS_NUMBER = env("SMS_NUMBER")
# SMS_SERVICE_ID = env("SMS_SERVICE_ID")
# SMS_SECRET_KEY = env("SMS_SECRET_KEY")
# SMS_ACCESS_KEY = env("SMS_ACCESS_KEY")

# ADDRESS_KEY = env("SEARCH_ADDRESS")
# SEARCH_KEY = env("SEARCH_KEY")

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST = env("EMAIL_HOST")
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# IAP_APPLE_SHARED_SECRET = env("IAP_APPLE_SHARED_SECRET")
# GOOGLE_SERVICE_ACCOUNT_JSON = env('GOOGLE_SERVICE_ACCOUNT_JSON')
# GOOGLE_PLAY_API_KEY = env('GOOGLE_PLAY_API_KEY')
# TRUSTED_IAP_IPS = env('TRUSTED_IAP_IPS').split(',')



SYSTEM_APP = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_celery_beat",
]

PROJECT_APP = [
    "users.apps.UsersConfig",
    "common.apps.CommonConfig",
]

THIRD_PARTY = [
    "rest_framework",   
]

INSTALLED_APPS = SYSTEM_APP + PROJECT_APP + THIRD_PARTY

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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


ASGI_APPLICATION ="config.asgi.application"
WSGI_APPLICATION ="config.wsgi.application"



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST', default='db') if not DEBUG else "localhost",
        'PORT': '5432',
    }
}




REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "config.authentication.JWTauthetication",
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute', 
        'user': '1000/day',   
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



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



LANGUAGE_CODE = "ko-kr"
TIME_ZONE = CELERY_TIMEZONE
USE_I18N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_DIRS =[BASE_DIR / "static",]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "django.db.backends": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#         },
#     },
# }


