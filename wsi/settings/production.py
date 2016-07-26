from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ''

DEBUG = True
THUMBNAIL_DEBUG = DEBUG

# COMPRESS_ENABLED = True

# ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS += (
    # 'django-debug-toolbar',
    'mailchimp',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'api_db',
        'USER': 'api_user',
        'PASSWORD': 'api_user',
        'HOST': 'localhost',
        'PORT': ''
    }
}

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMIN_EMAIL = 'admin@windshieldink.com'
ADMIN_ABUSE_EMAIL = 'abuse@windshieldink.com'
ADMIN_MESSENGER_EMAIL = 'messanger@windshieldink.com'
ADMIN_NOREPLY_EMAIL = 'no-reply@windshieldink.com'
ADMIN_SUPPORT_EMAIL = 'support@windshieldink.com'
FROM_EMAIL = 'no-reply@windshieldink.com'
TWILIO_DEFAULT_CALLERID = '+16473602666'

MANDRILL_ACCOUNT = 'U3xMfNawRKdattabtRv00g'
TWILIO_ACCOUNT_SID = 'AC9955f8d13a87d1b8326573abf9c29852'
TWILIO_AUTH_TOKEN = 'c6858173d9e8be6ad73d0f6c9f14a997'
GCM_TOKEN = 'AIzaSyD4l0G7eP5yCVAnevz1f_jhO_KZ5yZ1Z4k'
MAILCHIMP_API_KEY = '33e18096df3d2bc9fe9fd2b6dc6ba020-us12'
MAILCHIMP_WEBHOOK_KEY = ''
MAILCHIMP_LISTID = '4426c381aa'

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
    # ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
    # ('text/x-scss', 'sass --style compressed {infile} {outfile}'),
)

SESSION_KEY_ROTATION_TIME_INTERVAL = 1800
SERVER_HOST_NAME = 'api.windshieldink.com'
HARTBEAT_TIME_INTERVAL = 10 * 60
HARTBEAT_PARAMETER_NAME = "last_hartbeat_at"
ONLINE_PARAMETER_NAME = "online"
GCM_ACTION_KEY_PASSWORD_CHANGED = "app.wsi.PASSWORD_CHANGED"
GCM_PASSWORD_KEY = "pw"

# https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    # 'google.com',
    # 'hostname.example.com'
)
CORS_ORIGIN_REGEX_WHITELIST = (
    # '^(https?://)?(\w+\.)?google\.com$',
)

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'token'
)

SPAM_FILTER_INTERVAL = 1 * 60 * 60   # 1 HOUR - 3600 seconds
SPAM_RESTRICTS = {
    'first': 5,
    'second': 100
}


PHONE_VERIFY_INTERVAL = 1 * 60 * 60

APN_SANDBOX = False
APN_CERT = os.path.join(BASE_DIR, 'keys/apns-pro-cert.pem')
APN_KEY = os.path.join(BASE_DIR, 'keys/apns-pro-key-noenc.pem')
