"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
=======
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
>>>>>>> a1bce15f9bbd5e24103d3767b036c122fb3d5b86
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
