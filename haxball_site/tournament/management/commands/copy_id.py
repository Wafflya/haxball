from django.core.management.base import BaseCommand
from django.db.models import Q

from ...models import League, TourNumber, Match, Team, Player, Achievements


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        ach = Achievements.objects.all()
        for i in ach:
            i.position_number = i.id
            i.save()