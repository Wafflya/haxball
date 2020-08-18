from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class PlayerPositions(models.Model):
    TOP_FORWARD = 'FWD_T'
    BOT_FORWARD = 'FWD_B'
    DEF_MIDDLE = 'DM'
    GOALKEEPER = 'GK'
    ANY = 'ANY'
    POSITION = (
        (TOP_FORWARD, 'Верхний нападающий'),
        (BOT_FORWARD, 'Нижний нападающий'),
        (DEF_MIDDLE, 'Опорник'),
        (GOALKEEPER, 'Вратарь'),
        (ANY, 'Не важна'),
    )
    position = models.CharField(max_length=20, choices=POSITION, default=ANY)

    def __str__(self):
        return self.position


class FreeAgent(models.Model):
    player = models.OneToOneField(User, verbose_name='Игрок', on_delete=models.CASCADE)
    description = models.TextField("Комментарий к заявке", blank=True)
    positions = models.ManyToManyField(PlayerPositions, related_name='players_on_pos', blank=False)

    def __str__(self):
        return 'CA {}'.format(self.player.username)

    def player_pos(self):
        return self.player_positions.positions

    class Meta:
        verbose_name = 'Свободный агент'
        verbose_name_plural = "Свободные агенты"



