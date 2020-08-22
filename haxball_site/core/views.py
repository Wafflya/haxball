import json
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Max
from django.db.models.functions import Coalesce
from django.http import HttpResponse, request
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from pytils.translit import slugify

from .forms import CommentForm, EditProfileForm, PostForm
from .models import Post, Profile, LikeDislike, Category, Themes, Comment


# Вьюха для списка постов

class PostListView(ListView):
    queryset = Post.objects.filter(category__is_official=True).order_by('-important', '-created', )
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'core/post/list.html'


# Смотреть все новости
class AllPostView(ListView):
    queryset = Post.objects.filter(category__is_official=True).order_by('-created')
    context_object_name = 'posts'
    paginate_by = 7
    template_name = 'core/post/all_posts_list.html'


# Вьюха для трансляций
class LivesView(ListView):
    try:
        category = Category.objects.get(slug='live')
    except:
        category = None
    queryset = Post.objects.filter(category=category)
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'core/lives/lives_list.html'


# Главная форума тута
class ForumView(ListView):
    queryset = Themes.objects.all()
    context_object_name = 'themes'
    template_name = 'core/forum/forum_main.html'


# Вьюха для списка постов в категории форума
class CategoryListView(DetailView):
    model = Category
    template_name = 'core/forum/post_list_in_category.html'
    context_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.object.posts_in_category.annotate(
            last_activity=Coalesce(Max('comments__created'), 'created')).order_by('-last_activity')

        paginat = Paginator(post_list, 6)
        page = self.request.GET.get('page')

        try:
            posts = paginat.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            posts = paginat.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginat.page(paginat.num_pages)

        context['posts'] = posts
        context['page'] = page

        return context


# post-create view
def post_new(request, slug):
    category = Category.objects.get(slug=slug)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.category = category
            print(category.title)
            post.slug = slugify(post.title)
            post.created = datetime.now()
            post.save()
            return redirect(category.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'core/forum/add_post.html', {'form': form, 'category': category})


# post-edit view
def post_edit(request, slug, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect(post.get_absolute_url())
    else:
        if request.user == post.author or request.user.is_superuser:
            form = PostForm(instance=post)
        else:
            return HttpResponse('Ошибка доступа')
    return render(request, 'core/forum/add_post.html', {'form': form})


# edit comment
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        if request.user == comment.author and (
                timezone.now() - comment.created < timezone.timedelta(minutes=10)) or request.user.is_superuser:
            form = CommentForm(request.POST, instance=comment)
        else:
            return HttpResponse('Ошибка доступа или время истекло')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            return redirect(comment.post.get_absolute_url())
        else:
            comment.delete()
            return redirect(comment.post.get_absolute_url())
    else:
        if request.user == comment.author and (
                timezone.now() - comment.created < timezone.timedelta(minutes=15)) or request.user.is_superuser:
            form = CommentForm(instance=comment)
        else:
            return HttpResponse('Ошибка доступа или время истекло')
    return render(request, 'core/post/edit_comment.html', {'post': comment.post, 'comment_form': form})


# Вьюха для фасткапов
class FastcupView(ListView):
    try:
        category = Category.objects.get(slug='fastcups')
    except:
        category = None
    queryset = Post.objects.filter(category=category).order_by('-created')
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'core/fastcups/fastcups_list.html'


# Список админов
class AdminListView(ListView):
    queryset = User.objects.filter(is_staff=True).order_by('id')
    context_object_name = 'users'
    template_name = 'core/admins/admin_list.html'


# Вьюха для турниров
class TournamentsView(ListView):
    try:
        category = Category.objects.get(slug='tournaments')
    except:
        category = None
    queryset = Post.objects.filter(category=category)
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'core/tournaments/tournaments_list.html'


# Вьюха для поста и комментариев к нему.
# С одной стороны удобно одним методом, с другой-хезе как правильно надо)
# Учитывая, что потом пост-комменты будут использоваться для форума.. Такие дела
def post_detail(request, slug, id):
    post = get_object_or_404(Post, slug=slug,
                             id=id)
    # List of active comments for this post

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        page = request.POST.get('page')
        print(page)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            if request.POST.get("parent", None):
                new_comment.parent_id = int(request.POST.get('parent'))
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return redirect(post.get_absolute_url() + '#r' + str(new_comment.id))
    else:
        post.views = F('views') + 1
        post.save()
        comment_form = CommentForm()

    comments_obj = Comment.objects.filter(post=post, parent=None)
    paginat = Paginator(comments_obj, 25)
    page = request.GET.get('page')

    try:
        post_comments = paginat.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        post_comments = paginat.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_comments = paginat.page(paginat.num_pages)

    return render(request,
                  'core/post/detail.html',
                  {'post': post,
                   'post_comments': post_comments,
                   'page': page,
                   'comment_form': comment_form})


# Вьюха для профиля пользователя MultipleObjectMixin
class ProfileDetail(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'core/profile/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prof = context['profile']
        prof.views = prof.views + 1
        prof.save()
        print(prof.views)
        return context


# class AddPost(DetailView):
#    def post(self, request, ):


class EditMyProfile(DetailView, View):
    model = Profile
    context_object_name = 'profile'
    template_name = 'core/profile/profile_edit.html'

    def post(self, request, pk, slug):
        profile = Profile.objects.get(slug=slug, id=pk)
        profile_form = EditProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile_form.save()
        return redirect(profile.get_absolute_url())


class VotesView(View):
    model = None  # Модель данных - Статьи или Комментарии
    vote_type = None  # Тип комментария Like/Dislike

    def post(self, request, id):
        obj = self.model.objects.get(id=id)
        # GenericForeignKey не поддерживает метод get_or_create
        try:
            likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id,
                                                  user=request.user)

            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
            result = True

        return HttpResponse(
            json.dumps({
                "result": result,
                "like_count": obj.votes.likes().count(),
                "dislike_count": obj.votes.dislikes().count(),
                "sum_rating": obj.votes.sum_rating()
            }),
            content_type="application/json"
        )
