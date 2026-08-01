import os

from celery import Celery

# Tell Celery which Django settings module to use
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "django_backend_basics.settings",
)

# Create the Celery application
app = Celery("django_backend_basics")

# Load Celery settings from Django settings.py
app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

# Automatically discover tasks.py files in installed apps
app.autodiscover_tasks()