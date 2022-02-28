from datetime import date, datetime

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.utils import timezone
from online_users.models import OnlineUserActivity

from ..models import Post, NewComment
from tournament.models import Team, League

register = template.Library()


@register.filter
def get_class(value):
    return value.__class__.__name__


@register.filter
def subtract(value, arg):
    return value - arg


# тег для поискса кармы юзера(профиля), будем писать в профиль
# !!Пока что ищет ток по комментам карму, хз, могу допилить и по постам!
# ! Добавил и по постам
"""
@register.inclusion_tag('core/include/profile/karma.html')
def karma(profile):
    s = 0
    samo = 0
    for comment in Comment.objects.filter(author=profile.name):
        s += comment.votes.sum_rating()
        samo += comment.votes.filter(user=profile.name, vote=1).count() - comment.votes.filter(user=profile.name,
                                                                                               vote=-1).count()
    for post in Post.objects.filter(author=profile.name):
        s += post.votes.sum_rating()
        samo += post.votes.filter(user=profile.name, vote=1).count() - post.votes.filter(user=profile.name,
                                                                                         vote=-1).count()
    print(profile.karma)
    profile.karma = s - samo
    profile.save(update_fields=['karma'])
    return {'k': s - samo}
"""


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


# @register.inclusion_tag('core/include/comment/can_edit.html')
@register.filter
def can_edit(comment):
    if timezone.now() - comment.created < timezone.timedelta(minutes=10):
        return True
    else:
        return False


@register.inclusion_tag('core/include/profile/last_actuvity.html')
def user_last_activity(user):
    try:
        a = OnlineUserActivity.objects.get(user=user)
        is_online = timezone.now() - a.last_activity < timezone.timedelta(minutes=15)
        print(is_online)
    except:
        return None
    return {'last_seen': a.last_activity,
            'is_online': is_online}


# Тег для отображения последней активности на форуме
@register.inclusion_tag('core/include/forum/last_activity_in_category.html')
def forum_last_activity(category):
    last_post = Post.objects.filter(category=category).order_by('-created').first()
    # obj = ContentType.objects.get_for_model(obj)
    last_comment = NewComment.objects.filter(content_type=ContentType.objects.get_for_model(Post),
                                             post_comments__category=category).order_by('-created').first()

    if last_comment == None and last_post == None:
        return {'last_act': None}
    elif last_comment == None:
        return {'last_act': last_post.created}
    elif last_post == None:
        return {'last_act': last_comment.created}
    else:
        if last_comment.created > last_post.created:
            return {'last_act': last_comment.created}
        else:
            return {'last_act': last_post.created}


# Сайдбар для пользователей онлайн(по дефолту 15 минут)
@register.inclusion_tag('core/include/sidebar_for_users.html')
def show_users_online(count):
    user_activity_objects = OnlineUserActivity.get_user_activities(time_delta=timezone.timedelta(minutes=5))
    users_online_count = user_activity_objects.count()
    users_online = (user.user for user in user_activity_objects)
    return {'users_online': users_online,
            'users_online_count': users_online_count}


# Сайд-бар для last activity (выводит последние оставленные комментарии
# но максимум 1 для каждого поста(если 3 коммента в одном посте были последними - выведет 1)
@register.inclusion_tag('core/include/sidebar_for_last_activity.html')
def show_last_activity(count=10):
    # Последняя активность ваще везде-везде
    a = NewComment.objects.order_by('-created')[:150]
    content = set()
    last = []
    for com in a:
        if len(content) >= count:
            break

        if com.content_object in content:
            continue
        else:
            last.append(com)
            content.add(com.content_object)

    return {'last_comments': last}
    # print(len(content))
    # last = list(content).sort(key=lambda x: x.created)
    # print(last)
    # a = NewComment.objects.values(content_object).distinct()
    # print(a)


"""
    last_com = []
    last_comments = Post.objects.annotate(last_comment=Max('comments__created')).order_by('-last_comment')
    for i in last_comments:
        if len(i.comments.all()) > 0:
            last_com.append(i.comments.order_by('created').last())
    return {'last_comments': last_com[:count]}
"""


# Топ лайков за ТЕКУЩИЙ день, неделя, месяц, год
@register.inclusion_tag('core/include/sidebar_for_top_comments.html')
def show_top_comments(count=5, for_year=2020):
    my_date = datetime.now()
    year, week, day_of_week = my_date.isocalendar()
    day = my_date.day
    month = my_date.month
    top_com_today = NewComment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year, created__month=month,
                                                                          created__day=day).order_by('-like_count')[
                    :count]
    top_com_month = NewComment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year,
                                                                          created__month=month).order_by('-like_count')[
                    :count]
    top_com_year = NewComment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=year).order_by('-like_count')[
                   :count]

    week_start = my_date - timezone.timedelta(days=day_of_week - 1, hours=my_date.hour, minutes=my_date.minute)

    week_end = my_date + timezone.timedelta(days=7 - day_of_week, hours=23 - my_date.hour, minutes=60 - my_date.minute)
    top_com_week = NewComment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__gt=week_start,
                                                                          created__lt=week_end).order_by('-like_count')[
                   :count]
    return {'top_comments_day': top_com_today,
            'top_comments_month': top_com_month,
            'top_comments_year': top_com_year,
            'top_comments_week': top_com_week, }


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


@register.inclusion_tag('core/include/teams_in_navbar.html')
def teams_in_navbar():
    l = League.objects.filter(championship__is_active=True, is_cup=False).order_by('priority')
    return {'leagues': l}
    """"
    all_teams = Team.objects.all()
    teams = []
    for t in all_teams:
        if len(t.get_active_leagues()) > 0:
            teams.append(t)
    return {'teams': teams}
"""
