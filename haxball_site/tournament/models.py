from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class FreeAgent(models.Model):
    player = models.OneToOneField(User, verbose_name='Игрок', on_delete=models.CASCADE)
    description = models.TextField("Комментарий к заявке", blank=True)
    TOP_FORWARD = 'FWD_T'
    BOT_FORWARD = 'FWD_B'
    DEF_MIDDLE = 'DM'
    GOALKEEPER = 'GK'
    ANY = 'ANY'
    NO = 'NO'
    POSITION = (
        (TOP_FORWARD, 'Верхний нападающий'),
        (BOT_FORWARD, 'Нижний нападающий'),
        (DEF_MIDDLE, 'Опорник'),
        (GOALKEEPER, 'Вратарь'),
        (ANY, 'Не важна'),
    )
    position_main = models.CharField(max_length=20, choices=POSITION, default=ANY)
    POSITION = POSITION + ((NO, 'Отсутствует'),)
    position_second = models.CharField(max_length=20, choices=POSITION, default=NO)

    def __str__(self):
        return 'CA {}'.format(self.player.username)

    def player_pos(self):
        return self.player_positions.positions

    class Meta:
        verbose_name = 'Свободный агент'
        verbose_name_plural = "Свободные агенты"
