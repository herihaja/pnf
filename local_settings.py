SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'pnf',
        'USER': 'rova',
        'PASSWORD': 'rova',
        'HOST': '',
        'PORT': '',
    }
}
#GEOS_LIBRARY_PATH = '/Library/Frameworks/GEOS.framework/GEOS'