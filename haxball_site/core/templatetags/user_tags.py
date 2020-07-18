
from django import template
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from pytils.translit import slugify

from ..models import Profile

register = template.Library()


@register.inclusion_tag('core/include/sidebar_for_users.html')
def show_users_online(count=5):
    users_online = User.objects.filter(is_active=True).order_by('-date_joined')[:count]
    return {'users_online': users_online}


@register.simple_tag()
def create_profile(user):
    profile = Profile(name=user, slug=slugify(user.username))
    profile.save()
    return ''

