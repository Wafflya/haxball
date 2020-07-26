from django import template
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models import Max
from django.utils import timezone

from ..models import Post, Comment

register = template.Library()


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
        last_com.append(i.comments.order_by('-created').last())
    return {'last_comments': last_com}


# Чтобы топ по лайкам за период считал(период добавить)
@register.inclusion_tag('core/include/sidebar_for_top_comments.html')
def show_top_comments(count=5, for_year=2020):
    top_com = Comment.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=2020).order_by('-like_count')[
              :count]
    return {'top_comments': top_com}


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
    if x.days > 1:
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
