from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import localdate

from agenda.models import Event, Interest

EVENTS = [
    ("Джаз под куполом", "Камерный зал", 2, 900, 12, ["Музыка"],
     "Вечер живой музыки. В программе джазовые стандарты и импровизации."),
    ("Выставка «Город в деталях»", "Городская галерея", 3, 350, 0, ["Искусство"],
     "Фотографии городских улиц, афиши и повседневные предметы разных десятилетий."),
    ("Читка новой пьесы", "Малая сцена", 5, 0, 16, ["Театр", "Литература"],
     "Актёры читают современную пьесу, затем обсуждают её со зрителями."),
    ("Кино и музыка", "Кинозал", 7, 550, 12, ["Кино", "Музыка"],
     "Короткометражные фильмы в сопровождении живого фортепиано."),
    ("Графика и звук", "Выставочный зал", 9, 650, 12, ["Искусство", "Музыка"],
     "Звуковые инсталляции и авторская графика в одном пространстве."),
    ("Читаем вслух", "Городская библиотека", 11, 0, 6, ["Литература"],
     "Открытая встреча читательского клуба и обмен любимыми книгами."),
    ("История кинокостюма", "Музейная студия", 13, 550, 6, ["Кино", "Искусство"],
     "Разбор костюмов из кино с примерами эскизов и работы художника."),
    ("Спектакль «Ночной трамвай»", "Театральная студия", 15, 1800, 18, ["Театр"],
     "Камерный спектакль о случайных попутчиках в ночном городе."),
]


class Command(BaseCommand):
    help = "Добавляет учебную афишу с датами относительно текущего дня"

    @transaction.atomic
    def handle(self, *args, **options):
        added = 0
        today = localdate()
        for name, venue, offset, price, age, names, description in EVENTS:
            interests = [Interest.objects.get_or_create(name=tag)[0] for tag in names]
            event = Event.objects.filter(name=name, venue=venue).first()
            if event is None:
                event = Event.objects.create(
                    name=name, venue=venue, date=today+timedelta(days=offset),
                    price=price, min_age=age, description=description,
                )
                event.interests.set(interests)
                added += 1
        self.stdout.write(self.style.SUCCESS(f"Добавлено событий: {added}"))
