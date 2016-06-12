import env

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'webui',
    'social.apps.django_app.default',
    'social_orcid',
)

#if env.DEV_ENV:
#    INSTALLED_APPS += (
#        debug_toolbar',
#    )
