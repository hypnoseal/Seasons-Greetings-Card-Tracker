"""
WSGI config for Seasons_Greetings project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/home/protected')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Seasons_Greetings.settings')

application = get_wsgi_application()

