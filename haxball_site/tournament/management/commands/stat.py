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
        tp_matches = []
        for m in matches:
            all_goals = m.score_home + m.score_guest

            goals_scored = m.match_goal.count()+m.match_event.filter(event='OG').count()

            print(all_goals, goals_scored)
            if goals_scored == all_goals:
                norm_matches.append(m)
            else:
                tp_matches.append(m)
        print('norm',len(norm_matches))
        print('TP', len(tp_matches))
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

        print('stata')
        print(score_red, score_blue)
        print(win_red,draws,win_blue)
        print('Goals')
        print(goals)
        print(league)
        print('The End')
