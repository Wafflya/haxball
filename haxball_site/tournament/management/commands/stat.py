from django.core.management.base import BaseCommand

from ...models import League, TourNumber, Match, Team, Player


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        try:
            league = League.objects.get(championship__is_active=True, is_cup=False)
        except:
            print('Ошибка выбора лиги')
        matches = Match.objects.filter(league=league, is_played=True)
        teams = league.teams.all()
        # print(matches)
        norm_matches = []
        tp_matches = []
        for m in matches:
            all_goals = m.score_home + m.score_guest

            goals_scored = m.match_goal.count() + m.match_event.filter(event='OG').count()

            if goals_scored == all_goals:
                norm_matches.append(m)
            else:
                tp_matches.append(m)
        print('norm', len(norm_matches))
        print('TP', len(tp_matches))
        # Scores red/blue
        score_red = 0
        score_blue = 0
        win_red = 0
        win_blue = 0
        draws = 0
        goals = [0 for _ in range(16)]
        # goals - og count
        goals_not_og = 0
        goals_with_assist = 0
        og = 0
        for m in norm_matches:

            goals_not_og += m.match_goal.count()
            for g in m.match_goal.all():
                if g.assistent:
                    goals_with_assist += 1
            og += m.match_event.filter(event='OG').count()

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

        print(league)
        print('stata')
        print(score_red, score_blue)
        print(win_red, draws, win_blue)
        print('OG', og)
        print('Goals not og', goals_not_og)
        print('Goals with assits', goals_with_assist)
        print('Goals in timeline')
        print(goals)
        print('')

        """
        #Stat for each team
        for t in teams:
            score_red = 0
            score_blue = 0
            win_red = 0
            win_blue = 0
            draws = 0
            goals = [0 for _ in range(16)]
            # goals - og count
            goals_not_og = 0
            goals_with_assist = 0
            og = 0
            og_opp = 0
            matches_played = 0
            for m in norm_matches:
                if m.team_home == t or m.team_guest == t:
                    matches_played += 1
                    goals_not_og += m.match_goal.filter(team=t).count()
                    for g in m.match_goal.all():
                        if g.assistent and g.team == t:
                            goals_with_assist += 1
                    og += m.match_event.filter(event='OG', team=t).count()
                    og_opp = og_opp + (m.match_event.filter(event='OG').count() - m.match_event.filter(event='OG', team=t).count())

                    if t == m.team_home:
                        score_red += m.score_home
                    else:
                        score_blue += m.score_guest
                    if m.score_home > m.score_guest and m.team_home == t:
                        win_red += 1
                    elif m.score_home < m.score_guest and m.team_guest == t:
                        win_blue += 1
                    else:
                        draws += 1

                    for goal in m.match_goal.all():
                        if goal.team == t:
                            goals[goal.time_min] += 1
                    for own_goal in m.match_event.filter(event='OG').all():
                        if own_goal.team != t:
                            goals[goal.time_min] += 1

            if score_blue+score_red != 0:
                og_opp_percent = (og_opp/(score_red+score_blue))*100

            print('Статистика ', t)
            print('Матчей сыграно', matches_played)
            print('Голов забито(с АГ сопов)', score_blue+score_red)
            print('Голов красными - синими', score_red, score_blue)
            print('Побед красными, побед синими', win_red, win_blue)
            print('Автоголов в матче(своих)', og)
            print('Автоголов в матче(соперника)', og_opp)
            print('Процент Автоголов в матче (соперника)', round(og_opp_percent, 2))
            print('Голы, не автоголы ', goals_not_og)
            print('Голы с ассистированием', goals_with_assist)
            print('Процент голов с ассистами', round(100*goals_with_assist/goals_not_og, 2))
            print('Распределение голов по ходу матча')
            print(goals)
            print('')
        """

        players = Player.objects.all()

        dict = {}
        for p in players:
            secs_in_match = 0
            for m in norm_matches:
                vishel = m.match_substitutions.filter(player_in=p).count()
                ushel = m.match_substitutions.filter(player_out=p).count()
                if (p in m.team_home_start.all()) or (p in m.team_guest_start.all()):
                    if vishel == 0 and ushel == 0:
                        secs_in_match += 960
                    elif vishel == 0 and ushel == 1:
                        sub_out = m.match_substitutions.get(player_out=p)
                        secs_in_match += sub_out.time_min * 60 + sub_out.time_sec
                    elif vishel == 1 and ushel == 1:
                        sub_out = m.match_substitutions.get(player_out=p)
                        sub_in = m.match_substitutions.get(player_in=p)
                        secs_in_match += (sub_out.time_min * 60 + sub_out.time_sec) + (
                                960 - (sub_in.time_min * 60 + sub_in.time_sec))
                    elif vishel == 1 and ushel == 2:
                        sub_in = m.match_substitutions.get(player_in=p)
                        subs_out = m.match_substitutions.filter(player_out=p).order_by('time_min', 'time_sec')
                        print(subs_out)
                        secs_in_match += (subs_out[0].time_min * 60 + subs_out[0].time_sec) + (
                                (subs_out[1].time_min - sub_in.time_min) * 60 + (
                                    subs_out[1].time_sec - sub_in.time_sec))
                else:
                    if vishel == 1 and ushel == 0:
                        sub_in = m.match_substitutions.get(player_in=p)
                        secs_in_match += 960 - (sub_in.time_min * 60 + sub_in.time_sec)
                    elif vishel == 1 and ushel == 1:
                        sub_out = m.match_substitutions.get(player_out=p)
                        sub_in = m.match_substitutions.get(player_in=p)
                        secs_in_match += (
                                    (sub_out.time_min - sub_in.time_min) * 60 + (sub_out.time_sec - sub_in.time_sec))
                    elif vishel == 2 and ushel == 1:
                        subs_in = m.match_substitutions.filter(player_in=p).order_by('time_min', 'time_sec')
                        sub_out = m.match_substitutions.get(player_out=p)
                        secs_in_match += ((sub_out.time_min - subs_in[0].time_min) * 60 + (
                                    sub_out.time_sec - subs_in[0].time_sec)) + (960 - (subs_in[1].time_min*60 + subs_in[1].time_sec))
            dict[p] = secs_in_match
        l = sorted(dict, key=lambda x: dict[x], reverse=True)
        for i in l:
            print(i, dict[i])
        print('')

        print('The End')
