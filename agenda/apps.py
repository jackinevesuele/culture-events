from django.apps import AppConfig
from django.db.backends.signals import connection_created


def register_casefold(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "CASEFOLD", 1, str.casefold, deterministic=True,
        )


class AgendaConfig(AppConfig):
    name = "agenda"
    verbose_name = "Культурная афиша"

    def ready(self):
        connection_created.connect(register_casefold, dispatch_uid="agenda.casefold")
