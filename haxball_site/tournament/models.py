from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# Create your models here.
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField


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
    is_active = models.BooleanField('Текущий')
    created = models.DateTimeField('Создана', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'


class League(models.Model):
    title = models.CharField('Название лиги', max_length=128)
    priority = models.SmallIntegerField('Приоритет лиги', help_text='0-кубок, 1-высшая, 2-пердив, 3-втордив',)
    slug = models.SlugField(max_length=250)
    created = models.DateTimeField('Создана', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турнир'


class Team(models.Model):
    title = models.CharField('Название', max_length=128)
    slug = models.SlugField('слаг', max_length=250)
    date_found = models.DateField('Дата основания', default=date.today, )
    short_title = models.CharField('Сокращение', max_length=4)
    logo = models.ImageField('Логотип', upload_to='team_logos/', blank=True, null=True)
    owner = models.ForeignKey(User, verbose_name='Владелец', null=True, on_delete=models.SET_NULL,
                              related_name='team_owner')
    league = models.ForeignKey(League, verbose_name='Лига в которой играет', null=True, on_delete=models.SET_NULL,
                               related_name='teams_in_league', )
    office_link = models.URLField('Офис', blank=True)
    rating = models.SmallIntegerField('Рейтинг команды')

    def __str__(self):
        return 'Команда {}'.format(self.title)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Player(models.Model):
    name = models.OneToOneField(User, verbose_name='Никнейм игрока', null=True, on_delete=models.SET_NULL,
                                related_name='user_player')
    team = models.ForeignKey(Team, verbose_name='Команда', related_name='players_in_team', blank=True, null=True,
                             on_delete=models.SET_NULL)
    RUSSIA = 'RU'
    UKRAINE = 'UA'
    KAZAKHSTAN = 'KZ'
    BELARUS = 'BY'
    LATVIA = 'LV'
    PLAYER_NATION = [
        (RUSSIA, 'Россия'),
        (UKRAINE, 'Украинка'),
        (KAZAKHSTAN, 'Казахстан'),
        (BELARUS, 'Беларусь'),
        (LATVIA, 'Латвия'),
    ]
    nation = models.CharField(max_length=2, choices=PLAYER_NATION, default=RUSSIA, )

    JUST_PLAYER = 'PL'
    CAPTAIN = 'C'
    ASSISTENT = 'AC'
    ROLES = [
        (JUST_PLAYER, 'Игрок'),
        (CAPTAIN, 'Капитан'),
        (ASSISTENT, 'Ассистент')
    ]

    role = models.CharField(max_length=2, choices=ROLES, default=JUST_PLAYER, )

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


class Match(models.Model):
    league = models.ForeignKey(League, verbose_name='В лиге', related_name='matches_in_league',
                               on_delete=models.CASCADE)
    tour_num = models.SmallIntegerField(verbose_name='Номер тура')
    match_date = models.DateField('Дата матча', default=None, blank=True)
    replay_link = models.URLField('Ссылка на реплей', blank=True)
    inspector = models.ForeignKey(User, verbose_name='Проверил', limit_choices_to={'is_staff': True},
                                  on_delete=models.SET_NULL, null=True, )
    updated = models.DateTimeField('Обновлено', auto_now=True)
    team_home = ChainedForeignKey(Team, chained_field='league', chained_model_field='league', on_delete=models.CASCADE,
                                  related_name='home_matches', verbose_name='Хозяева')
    team_guest = ChainedForeignKey(Team, chained_field='league', chained_model_field='league', on_delete=models.CASCADE,
                                   related_name='guest_matches', verbose_name='Гости')

    team_home_start = ChainedManyToManyField(Player, related_name='player_in_start_home', horizontal=True,
                                             verbose_name='Состав хозяев', chained_field='team_home',
                                             chained_model_field='team', blank=True)

    team_guest_start = ChainedManyToManyField(Player, horizontal=True,
                                              verbose_name='Состав Гостей', chained_field='team_guest',
                                              chained_model_field='team', blank=True)
    is_played = models.BooleanField('Сыгран', default=False)

    def __str__(self):
        return 'Матч между {} и {}'.format(self.team_home, self.team_guest)

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['tour_num']


class Goal(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_goal',
                              on_delete=models.CASCADE)

    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Команда забила',
                             chained_model_field='league__matches_in_league', null=True,
                             on_delete=models.SET_NULL)

    author = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Автор гола',
                               related_name='goals', null=True,
                               on_delete=models.SET_NULL)
    assistent = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Ассистент',
                                  related_name='assists', blank=True, null=True,
                                  on_delete=models.SET_NULL)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    def __str__(self):
        return 'на {}:{} от {}({}) в {}'.format(self.time_min, self.time_sec, self.author, self.assistent, self.match)

    class Meta:
        verbose_name = 'Гол'
        verbose_name_plural = 'Голы'
        ordering = ['time_min', 'time_sec']


class Substitution(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_substitutions', null=True,
                              on_delete=models.SET_NULL)

    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Замена в команде',
                             chained_model_field='league__matches_in_league', null=True,
                             on_delete=models.SET_NULL)

    player_out = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Ушёл',
                                   related_name='replaced', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    player_in = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Вышел',
                                  related_name='join_game', blank=True, null=True,
                                  on_delete=models.SET_NULL)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    def __str__(self):
        return 'в {}:{} {} на {}'.format(self.time_min, self.time_sec, self.player_out, self.player_in)

    class Meta:
        verbose_name = 'Замена'
        verbose_name_plural = 'Замены'


class OtherEvents(models.Model):
    match = models.ForeignKey(Match, verbose_name='Матч', related_name='match_event', null=True,
                              on_delete=models.SET_NULL)
    team = ChainedForeignKey(Team, chained_field='match', verbose_name='Команда',
                             chained_model_field='league__matches_in_league', null=True,
                             on_delete=models.SET_NULL)
    author = ChainedForeignKey(Player, chained_field='team', chained_model_field='team', verbose_name='Автор',
                               related_name='event', null=True,
                               on_delete=models.SET_NULL)
    time_min = models.SmallIntegerField('Минута')
    time_sec = models.SmallIntegerField('Секунда')

    YELLOW_CARD = 'YEL'
    RED_CARD = 'RED'
    CLEAN_SHIT = 'CLN'
    OWN_GOALS = 'OG'
    EVENT = [
        (YELLOW_CARD, 'Жёлтая'),
        (RED_CARD, 'Красная'),
        (CLEAN_SHIT, 'Сухой матч'),
        (OWN_GOALS, 'Автогол'),
    ]

    event = models.CharField(max_length=3, choices=EVENT, default=CLEAN_SHIT)

    def __str__(self):
        return '{}:{} {} в {}'.format(self.time_min, self.time_sec, self.event, self.match)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
