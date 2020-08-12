from datetime import date, datetime

from django import template
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models import Max
from django.utils import timezone

from ..models import Post, Comment

register = template.Library()


# тег для поискса кармы юзера(профиля), будем писать в профиль
# !!Пока что ищет ток по комментам карму, хз, могу допилить и по постам!
# ! Добавил и по постам
@register.inclusion_tag('core/include/profile/karma.html')
def karma(profile):
    s = 0
    for comment in Comment.objects.filter(author=profile.name):
        s += comment.votes.sum_rating()
    for post in Post.objects.filter(author=profile.name):
        s += post.votes.sum_rating()
    return {'k': s}

# Упоролся и написал своё вычисление возраста 1 цифрой, т.к. встроенный
# таймсинс обрезает с месяцами... хз, надо доработать будет, чтобы писало возраст красиво, но хз зачем так из-за такой
# мелочи упарываться
@register.simple_tag
def age(born_date):
    if date.today().month > born_date.month:
        return (date.today().year - born_date.year)
    elif born_date.month == date.today().month and date.today().day > born_date.day:
        return date.today().year - born_date.year
    else:
        return date.today().year - born_date.year - 1


# Тег для отображения последней активности на форуме
@register.inclusion_tag('core/include/forum/last_activity_in_category.html')
def forum_last_activity(category):
    last_post = Post.objects.filter(category=category).order_by('-created').first()
    last_comment = Comment.objects.filter(post__category = category).order_by('-created').first()
    if last_comment == None and last_post==None:
        return {'last_act':None}
    elif last_comment == None:
        return {'last_act':last_post.created}
    elif last_post == None:
        return {'last_act':last_comment.created}
    else:
        if last_comment.created > last_post.created:
            return {'last_act': last_comment.created}
        else:
            return {'last_act': last_post.created}


# Вообще, это ласт-реги, но надо будет сделать куррент онлайн
@register.inclusion_tag('core/include/sidebar_for_users.html')
def show_users_online(count=5):
    users_online = User.objects.filter(is_active=True).order_by('-date_joined')[:count]
    return {'users_online': users_online}


# Сайд-бар для last activity (выводит последние оставленные комментарии
# но максимум 1 для каждого поста(если 3 коммента в одном посте были последними - выведет 1)
@register.inclusion_tag('core/include/sidebar_for_last_activity.html')
def show_last_activity(count=10):
    last_com = []
    last_comments = Post.objects.annotate(last_comment=Max('comments__created')).order_by('-last_comment')[:count]
    for i in last_comments:
        if len(i.comments.all()) >0:
            last_com.append(i.comments.order_by('-created').last())
    return {'last_comments': last_com}


# Чтобы топ по лайкам за период считал(!!!период добавить!!!)
@register.inclusion_tag('core/include/sidebar_for_top_comments.html')
def show_top_comments(count=5, for_year=2020):
    my_date = datetime.now()
    year, week, day_of_week = my_date.isocalendar()
    day = my_date.day
    month = my_date.month
    top_com_today = Comment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year, created__month=month, created__day=day).order_by('-like_count')[
              :count]
    top_com_month = Comment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year, created__month=month).order_by('-like_count')[
                    :count]
    top_com_year = Comment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year).order_by('-like_count')[
                    :count]
    return {'top_comments_day': top_com_today,
            'top_comments_month':top_com_month,
            'top_comments_year':top_com_year}


# Сайд-бар для отображеня топа лайков постов за всё время
# (Потом надо будет переделать, чтобы в параметр передавать за какое время, для переключения)
@register.inclusion_tag('core/include/sidebar_for_likes.html')
def show_post_with_top_likes(count=5):
    posts = Post.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=2020).order_by('-like_count')[
            :count]

    return {'liked_posts': posts}


# Фильтр, возращающий свежий ли пост или нет в зависимости от оффсета
@register.filter
def is_fresh(value, hours):
    x = timezone.now() - value
    if x.days >= 1:
        return False
    else:
        sec = 3600 * hours
        return x.seconds < sec


# Фильтр для проверки юзера в объекте(Типа, если лайк уже ставил или диз)
# except на ТайпЕррор, надо бы добавить, а то НоН обжект хэв но филтер ёба
@register.filter
def user_in(objects, user):
    if user.is_authenticated:
        try:
            return objects.filter(user=user).exists()
        except:
            return False
    return False
