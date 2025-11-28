from django.apps import AppConfig


class ObatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "obat"
    verbose_name = "Manajemen Obat & Resep"

    def ready(self):
        # Tempat untuk future signals (kalau nanti perlu)
        # from . import signals
        pass
