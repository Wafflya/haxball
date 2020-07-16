from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView

from .models import Post, Profile


# Вьюха для списка постов

class PostListView(ListView):
    queryset = Post.objects.all().order_by('-created')
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'core/post/list.html'

    # def post_list(request):
    #    posts = Post.objects.all()
    #    return render(request,
    #                  'core/post/list.html',
    #                  {'posts': posts})

    # class PostDetailView(DetailView):
    #    model = Post
    #    #slug_url_kwarg = {
    #    'slug': 'slug', 'publish__year':'year', 'publish__month':'month', 'publish__day':'day',
    #    }
    #    template_name = 'core/post/list.html'


# Вьюха для поста

def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post, slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'core/post/detail.html',
                  {'post': post})


class ProfileDetail(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'core/profile/profile_detail.html'