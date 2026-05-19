from django.core.management.base import BaseCommand

from portal.models import Room


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми залами'

    def handle(self, *args, **options):
        rooms = [
            {
                'name': 'Зал «Север»',
                'description': 'Просторный зал для всероссийских конференций до 300 участников.',
                'capacity': 300,
            },
            {
                'name': 'Зал «Волга»',
                'description': 'Средний зал с современным оборудованием, до 150 мест.',
                'capacity': 150,
            },
            {
                'name': 'Зал «Байкал»',
                'description': 'Камерный зал для региональных форумов, до 80 мест.',
                'capacity': 80,
            },
            {
                'name': 'Зал «Кавказ»',
                'description': 'Многофункциональный зал с переговорными комнатами, до 200 мест.',
                'capacity': 200,
            },
        ]
        for data in rooms:
            Room.objects.get_or_create(name=data['name'], defaults=data)
        self.stdout.write(self.style.SUCCESS('Тестовые залы добавлены.'))
