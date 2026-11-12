"""
Django settings for config project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Tự động nạp biến môi trường từ .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR.parent / ".env")
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

SECRET_KEY = 'django-insecure-c&^g(wp7@krvcx7r=-5nczx(6ays5kx$(x(jup^u3bkm7-$^z('

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'accounts',
    'academics',
    'documents',
    'permissions',
    'ai_search',
    'dashboard',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'frontend' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database: Tự động kết nối PostgreSQL khi có biến môi trường, fallback SQLite
db_url = os.getenv('DATABASE_URL', '')
db_name = os.getenv('POSTGRES_DB') or os.getenv('DB_NAME')

if db_url:
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=db_url)}
    except Exception:
        db_url = ''

if not db_url and db_name:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': os.getenv('POSTGRES_USER') or os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD') or os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('POSTGRES_HOST') or os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT') or os.getenv('DB_PORT', '5432'),
        }
    }
elif not db_url:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cloudflare R2 & File Storage Config (S3-compatible)
R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'docuni-documents')
R2_PUBLIC_DOMAIN = os.getenv('R2_PUBLIC_DOMAIN', '')
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 50 * 1024 * 1024))  # 50 MB
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.xlsx', '.zip']


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Auth redirects
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'


# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = '/static/'
_static_dir = BASE_DIR.parent / 'frontend' / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom Authentication Backend supporting both Django PBKDF2 and seed schema hashes
AUTHENTICATION_BACKENDS = [
    'accounts.auth_backend.DocUniAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]
