"""
WSGI config for socialpath project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialpath.settings')

application = get_wsgi_application()

from social.models import *
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social.settings")

