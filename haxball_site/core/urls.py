from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .models import Post, LikeDislike, Comment, Profile, NewComment
from tournament.models import League, Match

app_name = 'core'

urlpatterns = [
    # post views
    # path('', views.post_list, name='home'),
    path('', views.PostListView.as_view(), name='home'),
    path('post/<int:pk>/<slug:slug>', views.PostDetailView.as_view(), name='post_detail'),
    path('profile/<int:pk>/<slug:slug>/', views.ProfileDetail.as_view(), name='profile_detail'),
    # path('comment/<int:id>/<slug:slug>', views.AddComment.as_view(), name='add_comment'),
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
    path('forum/', views.ForumView.as_view(), name='forum'),
    path('forum/<slug:slug>', views.CategoryListView.as_view(), name='forum_category'),

    # Ссылка на создание нового поста на форуме
    path('forum/<slug:slug>/add_post', views.post_new, name='new_post'),

    # Создание нового "Правильного комментария" к профилю
    path('add_comment/profile/<int:pk>', views.AddCommentView.as_view(model=Profile), name='add_comment_profile'),
    # Создание нового "Правильного комментария" к лиге
    path('add_comment/league/<int:pk>', views.AddCommentView.as_view(model=League), name='add_comment_league'),
    # Создание нового "Правильного комментария" к посту
    path('add_comment/post/<int:pk>', views.AddCommentView.as_view(model=Post), name='add_comment_post'),
    # Создание нового "Правильного комментария" к матчу
    path('add_comment/match/<int:pk>', views.AddCommentView.as_view(model=Match), name='add_comment_match'),

    # Редактирование комментария
    path('post/edit_comment/<int:pk>', views.comment_edit, name='edit_comment'),

    # Удаление комментария
    path('delete_comment/<int:pk>', views.delete_comment, name='delete_comment'),

    # Редактирование поста, если создан пользователем
    path('post/<slug:slug>/<int:pk>/edit', views.post_edit, name='post_edit'),

    # Путь на самописный апи для обработку лайка/дизлайка ПОСТА через Ажакс-запрос
    path('api/post/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
         name='post_like'),
    path('api/post/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
         name='post_dislike'),

    # Путь на самописный апи для обработку лайка/дизлайка Комментария через Ажакс-запрос
    #    path('api/comment/<int:id>/like/',
    #         login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.LIKE)),
    #         name='comment_like'),
    #   path('api/comment/<int:id>/dislike/',
    #       login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE)),
    #      name='comment_dislike'),

    # Це пиздец госопода! Полный(
    #Путь на XYU
    path('api/comment/<int:id>/like/',
         login_required(views.VotesView.as_view(model=NewComment, vote_type=LikeDislike.LIKE)),
         name='comment_like'),
    path('api/comment/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=NewComment, vote_type=LikeDislike.DISLIKE)),
         name='comment_dislike'),

]
