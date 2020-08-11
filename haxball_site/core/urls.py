from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .models import Post, LikeDislike, Comment

app_name = 'core'

urlpatterns = [
    # post views
    # path('', views.post_list, name='home'),
    path('', views.PostListView.as_view(), name='home'),
    path('post/<int:id>/<slug:slug>',
         views.post_detail,
         name='post_detail'),
    path('profile/<int:pk>/<slug:slug>/', views.ProfileDetail.as_view(), name='profile_detail'),
    #path('comment/<int:id>/<slug:slug>', views.AddComment.as_view(), name='add_comment'),
    path('profile/<slug:slug>/<int:pk>/edit', views.EditMyProfile.as_view(), name='edit_profile'),

#  Путь к фасткапам
    path('fastcups/', views.FastcupView.as_view(), name='fastcups'),

#  Путь к турнирам
    path('tournaments/', views.TournamentsView.as_view(), name='tournaments'),

#  Путь к админам
    path('admin_list/', views.AdminListView.as_view(), name='admins'),

#  Правила

#  Все посты
    path('news_all/', views.AllPostView.as_view(), name='all_posts'),

#  Путь к трансляциям
    path('lives/', views.LivesView.as_view(), name='lives'),

#  Путь на форум
    path('forum/', views.ForumView.as_view(), name = 'forum'),
    path('forum/<slug:slug>', views.CategoryListView.as_view(), name='forum_category'),

# Ссылка на создание нового поста на форуме
    path('forum/<slug:slug>/add_post', views.post_new, name='new_post'),

# Редактирование профиля, если создан пользователем
    path('post/<slug:slug>/<int:pk>/edit', views.post_edit, name='post_edit'),

# Путь на самописный апи для обработку лайка/дизлайка ПОСТА через Ажакс-запрос
    path('api/post/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
         name='post_like'),
    path('api/post/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
         name='post_dislike'),

# Путь на самописный апи для обработку лайка/дизлайка Комментария через Ажакс-запрос
    path('api/comment/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.LIKE)),
         name='comment_like'),
    path('api/comment/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE)),
         name='comment_dislike'),

]
