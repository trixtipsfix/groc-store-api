import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY","dev")
DEBUG = os.getenv("DJANGO_DEBUG","True").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS","*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "rest_framework","rest_framework.authtoken","drf_spectacular","django_neomodel",
    "accounts","groceries","corsheaders"
]
CORS_ALLOW_ALL_ORIGINS = True
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "grocery_graph.urls"
TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates",
    "DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,
    "OPTIONS":{"context_processors":[
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "grocery_graph.wsgi.application"

DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}

NEOMODEL_NEO4J_BOLT_URL = os.getenv("NEOMODEL_NEO4J_BOLT_URL","bolt://neo4j:gr0c3rY$T0r3@localhost:7687")

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE="en-us"
TIME_ZONE=os.getenv("DJANGO_TIME_ZONE","Asia/Karachi")
USE_I18N=True
USE_TZ=True

STATIC_URL="/static/"
STATIC_ROOT = BASE_DIR/"staticfiles"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
from datetime import timedelta
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),"REFRESH_TOKEN_LIFETIME": timedelta(days=1),"SIGNING_KEY": SECRET_KEY}

SPECTACULAR_SETTINGS = {"TITLE":"Grocery Graph API","VERSION":"1.0.0","SERVE_INCLUDE_SCHEMA":False}
