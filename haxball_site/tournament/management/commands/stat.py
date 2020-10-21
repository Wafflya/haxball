from django.core.management.base import BaseCommand

from ...models import League, TourNumber, Match


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        try:
            league = League.objects.get(championship__is_active=True, is_cup=False)
        except:
            print('Ошибка выбора лиги')
        matches = Match.objects.filter(league=league, is_played=True)
        #print(matches)
        norm_matches = []
        for m in matches:
            if (m.team_home.title != 'ЦСКА' and m.team_guest.title != 'ЦСКА') and (
                    m.team_home.title != 'The Beatles' and m.team_guest.title != 'One more pass') and (
                    m.team_home.title != 'The Legendary Stars' and m.team_guest.title != 'KUMYS POWER'):
                norm_matches.append(m)
        # Scores red/blue
        score_red = 0
        score_blue = 0
        win_red = 0
        win_blue = 0
        draws = 0
        goals = [0 for _ in range(16)]
        for m in norm_matches:

            score_red += m.score_home
            score_blue += m.score_guest
            if m.score_home > m.score_guest:
                win_red += 1
            elif m.score_home < m.score_guest:
                win_blue += 1
            else:
                draws += 1

            for goal in m.match_goal.all():
                goals[goal.time_min] += 1

        print(score_red, score_blue)
        print(win_red,draws,win_blue)
        print('Goals')
        print(goals)
        print(league)
        print('The End')
