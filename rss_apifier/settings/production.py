import os

from .base import *

# Overall settings
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = [os.environ.get('SITENAME', 'localhost')]
PRODUCTION = True