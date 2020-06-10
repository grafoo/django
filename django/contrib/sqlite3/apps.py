from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Sqlite3Config(AppConfig):
    name = "django.contrib.sqlite3"
    verbose_name = _("SQLite extensions")

    # TODO: Register match lookup
    def ready(self):
        pass
