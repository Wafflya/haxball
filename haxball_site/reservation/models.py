from django.contrib.auth.models import User
from django.db import models
from tournament.models import Match


# Create your models here.
class ReservationHost(models.Model):
    name = models.CharField('Название хоста', max_length=256)
    link = models.URLField('Адрес')
    is_active = models.BooleanField('Активный')

    def __str__(self):
        return 'Хост {}'.format(self.name)

    class Meta:
        verbose_name = 'Хост'
        verbose_name_plural = 'Хосты'
        ordering = ['id']


class ReservationEntry(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор заявки', on_delete=models.CASCADE,
                               related_name='user_reservation_authors')
    match = models.OneToOneField(Match, verbose_name='На какой матч', on_delete=models.CASCADE,
                                 related_name='match_reservation')
    time_date = models.DateTimeField('На какое время')

    host = models.ForeignKey(ReservationHost, verbose_name='На каком хосте', on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Бронь матча {} на {}'.format(self.match, self.time_date.astimezone())

    class Meta:
        verbose_name = 'Бронь хоста'
        verbose_name_plural = 'Брони хоста'
        ordering = ['-time_date']