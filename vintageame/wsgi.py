"""
WSGI config for vintageame project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

from vintageame.wsgi__dev import *
from vintageame.wsgi__prod import *
