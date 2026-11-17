from __future__ import absolute_import, unicode_literals

import os

from celery import Celery



# Установка переменной окружения для настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')

# Создание экземпляра объекта Celery
app = Celery('my_project')

# Загрузка конфигураций из настроек Django с префиксом 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск и регистрация задач из файлов tasks.py во всех приложениях Django
app.autodiscover_tasks()
