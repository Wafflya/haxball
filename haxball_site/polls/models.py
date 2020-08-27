from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class Question(models.Model):
    title = models.CharField('Название', max_length=128)
    question_text = models.CharField('Текст вопроса', max_length=256)
    created = models.DateTimeField('Дата создания', default=timezone.now)
    is_active = models.BooleanField('Активен', default=False)
    anonymously = models.BooleanField('Анонимный', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField('Вариант ответа', max_length=256)
    votes = models.ManyToManyField(User, blank=True, related_name='user_votes',)

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = "Вариант"
        verbose_name_plural = "Варианты"
        ordering = ['id']


#class Votes(models.Model):
 #   user = models.ForeignKey(User, related_name='user_votes', on_delete=models.CASCADE)
  #  vote = models.ForeignKey(Choice, related_name='votes_for', on_delete=models.CASCADE)
#
 #   class Meta:
  #      verbose_name = "Голос"
   #     verbose_name_plural = "Голоса"