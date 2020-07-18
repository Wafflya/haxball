from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .models import Post, LikeDislike

app_name = 'core'

urlpatterns = [
    # post views
    # path('', views.post_list, name='home'),
    path('', views.PostListView.as_view(), name='home'),
    path('post/<int:id>/<slug:slug>',
         views.post_detail,
         name='post_detail'),
    path('profile/<slug:slug>', views.ProfileDetail.as_view(), name='profile_detail'),
    path('comment/<int:id>/<slug:slug>', views.AddComment.as_view(), name='add_comment'),
    path('profile/<slug:slug>/edit', views.EditMyProfile.as_view(), name='edit_profile'),
    path('api/post/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
         name='post_like'),
    path('api/post/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
         name='post_dislike'),

]
