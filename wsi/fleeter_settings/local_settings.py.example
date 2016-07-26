# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

from .base import *

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

SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.sqlite3'
}

# PAYPAL_IDENTITY_TOKEN = 'tw-P7uevIjrdGHMM-ZUKIgmbSROK4d0ri97WjbVVC9xeMnAzvIkWaEVTd_8'
PAYPAL_TEST = True

PAYPAL_RECEIVER_EMAIL = 'ken-facilitator@windshieldink.com'
# PAYPAL_MERCHANT_ID = 'S83B93C49HL9Q'

STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_Qe6JBa5Z5Ex6KjdRw91rHeDK")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_HXhrO1qa2Z3VPWIMzl6GaxNs")
