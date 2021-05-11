import datetime
import random
import time

from django.core.management.base import BaseCommand, CommandError

from ...models import League, TourNumber, Match, Season


class Command(BaseCommand):
    help = 'Считаем активность инспекторов'

    def add_arguments(self, parser):
        parser.add_argument('champ_number', default=0, nargs='?', type=int, )

    def handle(self, *args, **options):
        print(options['champ_number'])
        if options['champ_number'] == 0:
            print('Выборка по всем сезонам')
            all_matches = Match.objects.filter(is_played=True)
        else:
            try:
                ses = Season.objects.get(number=options['champ_number'])
            except:
                raise CommandError('Выбран несуществующий сезон')

            print('Выборка по сезону {}'.format(options['champ_number']))
            all_matches = Match.objects.filter(league__championship=ses, is_played=True)
        inspectors = {}
        all_goals = 0
        all_events = 0
        for m in all_matches:
            all_goals += m.match_goal.count()
            all_events += m.match_substitutions.count() + m.match_event.count()
            if m.inspector in inspectors.keys():
                inspectors[m.inspector].append(m)
            else:
                inspectors[m.inspector] = []
                inspectors[m.inspector].append(m)


        print("Инспектор  М  Г другое sum")
        for inspector in inspectors:
            goals_added = 0
            other_event_added = 0
            for m in inspectors[inspector]:
                goals_added += m.match_goal.count()
                other_event_added += m.match_substitutions.count()+m.match_event.count()
            percent = round(100*((goals_added+other_event_added)/(all_goals+all_events)),1)
            print(inspector,len(inspectors[inspector]), goals_added+other_event_added, percent)