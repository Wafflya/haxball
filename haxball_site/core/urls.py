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
    path('<slug:slug>/', views.StuffView.as_view(), name='fastcups'),
#  Путь на форум
    #path('forum/', )

# Самописный путь на апи обработку лайка/дизлайка ПОСТА
    path('api/post/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
         name='post_like'),
    path('api/post/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
         name='post_dislike'),

# Самописный путь на апи обработку лайка/дизлайка Комментария
    path('api/comment/<int:id>/like/',
         login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.LIKE)),
         name='comment_like'),
    path('api/comment/<int:id>/dislike/',
         login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE)),
         name='comment_dislike'),

]
