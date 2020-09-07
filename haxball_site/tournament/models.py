from datetime import date

from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField

#from django.db.models import

from core.models import NewComment


class FreeAgent(models.Model):
    player = models.OneToOneField(User, verbose_name='Игрок', on_delete=models.CASCADE, related_name='user_free_agent')
    description = models.TextField("Комментарий к заявке", max_length=200, blank=True)
    TOP_FORWARD = 'Верхний нападающий'
    BOT_FORWARD = 'Нижний нападающий'
    FORWARD = 'Нападающий'
    DEF_MIDDLE = 'Опорник'
    GOALKEEPER = 'Вратарь'
    BACK = 'Задняя линия'
    GK_FWD = 'Нападающий/вратарь'
    DM_FWD = 'Нападающий/опорник'
    ANY = 'Любая'
    POSITION = (
        (TOP_FORWARD, 'Верхний нападающий'),
        (BOT_FORWARD, 'Нижний нападающий'),
        (FORWARD, "Нападающий"),
        (DEF_MIDDLE, 'Опорник'),
        (GOALKEEPER, 'Вратарь'),
        (BACK, "Задняя линия"),
        (DM_FWD, 'Нападающий/Опорник'),
        (GK_FWD, 'Нападающий/Вратарь'),
        (ANY, 'Любая'),
    )
    position_main = models.CharField(max_length=20, choices=POSITION, default=ANY)
    created = models.DateTimeField("Оставлена", default=timezone.now)
    deleted = models.DateTimeField("Снята", auto_now_add=True)
    is_active = models.BooleanField("Активно", default=True)

    def __str__(self):
        return 'CA {}'.format(self.player.username)

    def player_pos(self):
        return self.player_positions.positions

    class Meta:
        verbose_name = 'Свободный агент'
        verbose_name_plural = "Свободные агенты"


#           Определние моделей для чемпионата (Чемпионат, команда, игрок, матч, событие )


class Season(models.Model):
    title = models.CharField('Название Розыгрыша', max_length=128)
    number = models.SmallIntegerField('Номер сезона')
    is_active = models.BooleanField('Текущий')
    created = models.DateTimeField('Создана', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'


class Team(models.Model):
    title = models.CharField('Название', max_length=128)
    slug = models.SlugField('слаг', max_length=250)
    date_found = models.DateField('Дата основания', default=date.today, )
    short_title = models.CharField('Сокращение', help_text='До 10 символов', max_length=11)
    logo = models.ImageField('Логотип', upload_to='team_logos/', default='team_logos/default.png')
    color_1 = ColorField(default='#FFFFFF', verbose_name='Цвет 1')
    color_2 = ColorField(default='#FFFFFF', verbose_name='Цвет 2')
    color_table = ColorField(default='#FFFFFF', verbose_name='Цвет Таблички')
    owner = models.ForeignKey(User, verbose_name='Владелец', null=True, on_delete=models.SET_NULL,
                              related_name='team_owner')
    # league = models.ForeignKey(League, verbose_name='Лига в которой играет', null=True, on_delete=models.SET_NULL,
    #                          related_name='teams_in_league', )
    office_link = models.URLField('Офис', blank=True)
    rating = models.SmallIntegerField('Рейтинг команды', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('tournament:team_detail', args=[self.slug])

    def get_active_leagues(self):
        return self.leagues.filter(championship__is_active=True)

    def __str__(self):
        return 'Команда {}'.format(self.title)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class League(models.Model):
    championship = models.ForeignKey(Season, verbose_name='Сезон', related_name='tournaments_in_season', null=True,
                                     on_delete=models.CASCADE)
    title = models.CharField('Название лиги', max_length=128)
    is_cup = models.BooleanField('Кубок', help_text='галочка, если кубок', default=False)
    priority = models.SmallIntegerField('Приоритет лиги', help_text='1-высшая, 2-пердив, 3-втордив',
                                        blank=True)
    slug = models.SlugField(max_length=250)
    created = models.DateTimeField('Создана', auto_now_add=True)
    teams = models.ManyToManyField(Team, related_name='leagues', verbose_name='Команды в лиге')
    comments = GenericRelation(NewComment, related_query_name='league_comments')
    commentable = models.BooleanField("Комментируемый турнир", default=True)

    def __str__(self):
        return '{}, {}'.format(self.title, self.championship)

    def get_absolute_url(self):
        return reverse('tournament:league', args=[self.slug])

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турнир'


class Nation(models.Model):
    country = models.CharField('Страна', max_length=100, )
    flag = models.ImageField('Флаг', upload_to='country_flag/')

    def __str__(self):
        return self.country

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class Player(models.Model):
    name = models.OneToOneField(User, verbose_name='Пользователь', null=True, blank=True,
                                on_delete=models.SET_NULL,
                                related_name='user_player')

    nickname = models.CharField('Никнейм игрока', max_length=150, )

    FORWARD = 'FW'
    DEF_MIDDLE = 'DM'
    GOALKEEPER = 'GK'
    POSITIONS = (
        (FORWARD, "Нападающий"),
        (DEF_MIDDLE, 'Опорник'),
        (GOALKEEPER, 'Вратарь'),
    )
    position = models.CharField("Позиция", max_length=2, choices=POSITIONS, null=True, blank=True)

    team = models.ForeignKey(Team, verbose_name='Команда', related_name='players_in_team', blank=True, null=True,
                             on_delete=models.SET_NULL)

    player_nation = models.ForeignKey(Nation, verbose_name='Национальность', related_name='country_players', null=True,
                                      on_delete=models.SET_NULL)
    JUST_PLAYER = 'PL'
    CAPTAIN = 'C'
    ASSISTENT = 'AC'
    ROLES = [
        (JUST_PLAYER, 'Игрок'),
        (CAPTAIN, 'Капитан'),
        (ASSISTENT, 'Ассистент')
    ]

    role = models.CharField("Должность", max_length=2, choices=ROLES, default=JUST_PLAYER, )

    def __str__(self):
        return '{}'.format(self.nickname)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class TourNumber(models.Model):
    number = models.SmallIntegerField('Номер тура')
    date_from = models.DateField('Дата тура с', default=date.today, blank=True, null=True)
    date_to = models.DateField('Дата тура по', default=date.today, blank=True, null=True)
    league = models.ForeignKey(League, verbose_name='В какой лиге', related_name='tours', on_delete=models.CASCADE)
    is_actual = models.BooleanField('Актуальный', default=False)

    def __str__(self):
        return '{}'.format(self.number)

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'
        ordering = ['number']


class Match(models.Model):
    league = models.ForeignKey(League, verbose_name='В лиге', related_name='matches_in_league',
                               on_delete=models.CASCADE)
    numb_tour = models.ForeignKey(TourNumber, verbose_name='Номер тура', related_name='tour_matches',
                                  on_delete=models.CASCADE, null=True, )
    match_date = models.DateField('Дата матча', default=None, blank=True, null=True)
    replay_link = models.URLField('Ссылка на реплей', blank=True)
    inspector = models.ForeignKey(User, verbose_name='Проверил', limit_choices_to={'is_staff': True},
                                  on_delete=models.SET_NULL, null=True, blank=True)
    updated = models.DateTimeField('Обновлено', auto_now=True)
    team_home = ChainedForeignKey(Team, chained_field='league', chained_model_field='leagues', on_delete=models.CASCADE,
                                  related_name='home_matches', verbose_name='Хозяева')
    team_guest = ChainedForeignKey(Team, chained_field='league', chained_model_field='leagues',
                                   on_delete=models.CASCADE,
                                   related_name='guest_matches', verbose_name='Гости')

    score_home = models.SmallIntegerField('Забито хозявами', default=0)
    score_guest = models.SmallIntegerField('Забито гостями', default=0)
    team_home_start = models.ManyToManyField(Player, related_name='player_in_start_home',
                                             verbose_name='Состав хозяев', blank=True)
    comments = GenericRelation(NewComment, related_query_name='match_comments')
    commentable = models.BooleanField("Комментируемый матч", default=True)

    # chained_field = 'team_home',
    # chained_model_field = 'team',

    team_guest_start = models.ManyToManyField(Player, related_name='player_in_start_guest',
                                              verbose_name='Состав Гостей', blank=True)

    # chained_field='team_guest',
    #                                               chained_model_field='team',
    is_played = models.BooleanField('Сыгран', default=False)

    comment = models.CharField('Комментарий к матчу', max_length=1024, blank=True, null=True)

    def __str__(self):
        return 'Матч {} - {}, {} тур'.format(self.team_home.short_title, self.team_guest.short_title, self.numb_tour)

    def get_absolute_url(self):
        return reverse('tournament:match_detail', args=[self.id])

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['numb_tour']


class Goal(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_goal', null=True, blank=True,
                              on_delete=models.CASCADE)

    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Команда забила', related_name='team_goals',
                             chained_model_field='leagues__matches_in_league', null=True,
                             on_delete=models.SET_NULL)

    author = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Автор гола',
                               related_name='goals', null=True,
                               on_delete=models.CASCADE)
    assistent = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Ассистент',
                                  related_name='assists', blank=True, null=True,
                                  on_delete=models.CASCADE)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    def save(self, *args, **kwargs):
        if self.match.team_home == self.team:
            self.match.score_home += 1
            self.match.save(update_fields=['score_home'])
        elif self.team == self.match.team_guest:
            self.match.score_guest += 1
            self.match.save(update_fields=['score_guest'])
        super(Goal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.match.team_home == self.team:
            self.match.score_home -= 1
            self.match.save(update_fields=['score_home'])
        elif self.team == self.match.team_guest:
            self.match.score_guest -= 1
            self.match.save(update_fields=['score_guest'])
        super(Goal, self).delete(*args, **kwargs)

    def __str__(self):
        return 'на {}:{} от {}({}) в {}'.format(self.time_min, self.time_sec, self.author, self.assistent, self.match)

    class Meta:
        verbose_name = 'Гол'
        verbose_name_plural = 'Голы'
        ordering = ['time_min', 'time_sec']


class Substitution(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_substitutions', null=True,
                              on_delete=models.CASCADE)

    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Замена в команде',
                             chained_model_field='leagues__matches_in_league', null=True,
                             on_delete=models.SET_NULL)

    player_out = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Ушёл',
                                   related_name='replaced', null=True,
                                   on_delete=models.CASCADE)
    player_in = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Вышел',
                                  related_name='join_game', null=True,
                                  on_delete=models.CASCADE)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    def __str__(self):
        return 'в {}:{} {} на {}'.format(self.time_min, self.time_sec, self.player_out, self.player_in)

    class Meta:
        verbose_name = 'Замена'
        verbose_name_plural = 'Замены'


class OtherEvents(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_event', null=True,
                              on_delete=models.CASCADE)
    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Команда',
                             chained_model_field='leagues__matches_in_league', null=True,
                             on_delete=models.SET_NULL)
    author = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Автор',
                               related_name='event', null=True,
                               on_delete=models.CASCADE)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    YELLOW_CARD = 'YEL'
    RED_CARD = 'RED'
    CLEAN_SHIT = 'CLN'
    OWN_GOALS = 'OG'
    EVENT = [
        (YELLOW_CARD, 'Жёлтая'),
        (RED_CARD, 'Красная'),
        (CLEAN_SHIT, 'Сухой тайм'),
        (OWN_GOALS, 'Автогол'),
    ]

    event = models.CharField(max_length=3, choices=EVENT, default=CLEAN_SHIT, verbose_name='Тип события')

    def save(self, *args, **kwargs):
        if self.match.team_home == self.team and self.event == 'OG':
            self.match.score_guest += 1
            self.match.save(update_fields=['score_guest'])
        elif self.team == self.match.team_guest and self.event == 'OG':
            self.match.score_home += 1
            self.match.save(update_fields=['score_home'])
        super(OtherEvents, self).save(*args, **kwargs)

    def __str__(self):
        return '{}:{} {} в {}'.format(self.time_min, self.time_sec, self.event, self.match)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class PlayerTransfer(models.Model):
    trans_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='teams_all', verbose_name='Игрок', )
    to_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_transfers', verbose_name='В команду',
                                blank=True, null=True)
    date_join = models.DateField(default=None)
    season_join = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name='В каком сезоне')

    def save(self, *args, **kwargs):
        if self.to_team:
            self.trans_player.team = self.to_team
            self.trans_player.save()
        else:
            print(self.trans_player)
            self.trans_player.team = None
            self.trans_player.save()
        super(PlayerTransfer, self).save(*args, **kwargs)

    def __str__(self):
        return 'Переход {} в команду {}'.format(self.trans_player, self.to_team)

    class Meta:
        verbose_name = 'Трансфер'
        verbose_name_plural = 'Трансферы'
