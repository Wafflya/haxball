from django import template
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from pytils.translit import slugify

from ..models import Profile, Post, Comment

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
    last_comments = Comment.objects.order_by('-created')[:count]
    #for com in last_comments:
        #print(com.post.title)
    return {'last_comments':last_comments}

# Сайд-бар для отображеня топа лайков постов за всё время
# (Потом надо будет переделать, чтобы в параметр передавать за какое время, для переключения)
@register.inclusion_tag('core/include/sidebar_for_likes.html')
def show_post_with_top_likes(count=5):
    posts = Post.objects.annotate(like_count=Count('votes', filter=Q(votes__vote__gt=0))).annotate(
        dislike_count=Count('votes', filter=Q(votes__vote__lt=0))).filter(created__year=2020).order_by('-like_count')[:count]
    # posts = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Post))
    # liked_posts = posts.likes()
    return {'liked_posts': posts}


#Фильтр, возращающий свежий ли пост или нет в зависимости от оффсета
@register.filter
def is_fresh(value, hours):
    x = timezone.now()-value
    if x.days > 1:
        return False
    else:
        sec = 3600*hours
        return x.seconds < sec