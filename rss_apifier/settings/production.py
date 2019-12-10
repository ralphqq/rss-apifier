import os

from .base import *

# Overall settings
DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = [os.environ['SITENAME']]
PRODUCTION = True