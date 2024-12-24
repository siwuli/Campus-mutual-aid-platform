# errands/apps.py

from django.apps import AppConfig

class ErrandsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'errands'

    def ready(self):
        import errands.signals  # 加载信号
