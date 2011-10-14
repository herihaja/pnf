SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'pnf',
        'USER': 'hni',
        'PASSWORD': 'hni',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}
GEOS_LIBRARY_PATH = '/Library/Frameworks/GEOS.framework/GEOS'