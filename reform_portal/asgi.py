"""
ASGI config for reform_portal project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reform_portal.settings')

application = get_asgi_application()
