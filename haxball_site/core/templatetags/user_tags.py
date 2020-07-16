from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('core/include/sidebar_for_users.html')
def show_users_online(count=5):
    users_online = User.objects.filter(is_active=True).order_by('-date_joined')
    return {'users_online': users_online}
