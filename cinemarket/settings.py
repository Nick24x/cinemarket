from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent



# SEGURIDAD
SECRET_KEY = 'django-insecure-b=@w%b$@utfdh93sa1(_zdwbkldsppq%sw7(r#)wcn1w1%##^r'
DEBUG = False

ALLOWED_HOSTS = [
    'cinemarket-production.up.railway.app',
    'localhost',
    '127.0.0.1',
]



# APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'arriendos',
    'usuarios',
    'peliculas',
    'reportes',
    'panel',
    'pagos',
]



# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'cinemarket.urls'



# TEMPLATES
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


WSGI_APPLICATION = 'cinemarket.wsgi.application'



# BASE DE DATOS — Supabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.ipvfsirzkjyyppcwkkwk',
        'PASSWORD': 'Nico2409.',
        'HOST': 'aws-1-us-east-2.pooler.supabase.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}



# PASSWORDS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True



# STATIC & MEDIA
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



# LOGIN
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'



# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://cinemarket-production.up.railway.app',
]



# MERCADO PAGO
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY")



# CORREO — USANDO RESEND
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DEFAULT_FROM_EMAIL = "CineMarket <onboarding@resend.dev>"



# AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
