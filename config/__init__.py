import json
from django.db.backends.signals import connection_created
from django.dispatch import receiver


@receiver(connection_created)
def extend_sqlite(sender, connection, **kwargs):
    """
    Ensure SQLite supports JSON_VALID function on Python versions with SQLite < 3.38.
    """
    if connection.vendor == 'sqlite':
        def json_valid(val):
            if val is None:
                return 1
            try:
                json.loads(val)
                return 1
            except Exception:
                return 0

        try:
            connection.connection.create_function("JSON_VALID", 1, json_valid)
        except Exception:
            pass
