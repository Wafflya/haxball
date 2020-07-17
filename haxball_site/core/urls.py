from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    # post views
    # path('', views.post_list, name='home'),
    path('', views.PostListView.as_view(), name='home'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',
         views.post_detail,
         name='post_detail'),
    path('profile/<slug:slug>', views.ProfileDetail.as_view(), name='profile_detail'),
    path('comment/<int:id>/<slug:slug>', views.AddComment.as_view(), name='add_comment')
]
