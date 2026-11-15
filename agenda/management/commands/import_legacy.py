import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from agenda.models import Event, Interest, Recommendation, Visitor
from db.database import DATABASE, connect


class Command(BaseCommand):
    help = "Переносит данные из базы SQLite ПР7 в пустую базу Django"

    def add_arguments(self, parser):
        parser.add_argument("--database-file", type=Path, default=DATABASE)

    @transaction.atomic
    def handle(self, *args, **options):
        if any(model.objects.exists() for model in (Interest, Visitor, Event, Recommendation)):
            raise CommandError("Для импорта требуется пустая база культурной афиши.")
        try:
            counts = self.import_rows(options["database_file"])
        except (sqlite3.Error, OSError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Перенос завершён: {counts}"))

    def import_rows(self, path):
        with connect(path) as source:
            interest_rows = source.execute("SELECT * FROM interests").fetchall()
            visitor_rows = source.execute("SELECT * FROM visitors").fetchall()
            event_rows = source.execute("SELECT * FROM events").fetchall()
            rec_rows = source.execute("SELECT * FROM recommendations").fetchall()
            Interest.objects.bulk_create(Interest(**row) for row in interest_rows)
            Visitor.objects.bulk_create(Visitor(**row) for row in visitor_rows)
            Event.objects.bulk_create(Event(**row) for row in event_rows)
            Visitor.interests.through.objects.bulk_create(
                Visitor.interests.through(**row)
                for row in source.execute("SELECT * FROM visitor_interests")
            )
            Event.interests.through.objects.bulk_create(
                Event.interests.through(**row)
                for row in source.execute("SELECT * FROM event_interests")
            )
            Recommendation.objects.bulk_create(Recommendation(**row) for row in rec_rows)
        return (len(interest_rows), len(visitor_rows), len(event_rows), len(rec_rows))
