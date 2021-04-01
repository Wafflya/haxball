import json
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Max
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from pytils.translit import slugify

from .forms import CommentForm, EditProfileForm, PostForm, NewCommentForm
from .models import Post, Profile, LikeDislike, Category, Themes, Comment, NewComment, IPAdress
from haxball_site import settings


# Вьюха для списка постов

class PostListView(ListView):
    queryset = Post.objects.filter(category__is_official=True).order_by('-important', '-created', )
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'core/post/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_imp = Post.objects.filter(category__is_official=True, important=True).count()
        context['count_imp'] = count_imp
        if self.request.user.is_authenticated:
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_a = x_forwarded_for
            else:
                if not settings.DEBUG:
                    ip_a = self.request.META.get('HTTP_X_REAL_IP')
                else:
                    ip_a = self.request.META.get('REMOTE_ADDR')

            try:
                ipp = IPAdress.objects.get(name=self.request.user, ip=ip_a)
                ipp.update = timezone.now()
                ipp.save(update_fields=['update'])
            except:
                IPAdress.objects.create(ip=ip_a, name=self.request.user)

            ips = IPAdress.objects.filter(ip=ip_a)
            if ips.count() > 1:
                for i in ips:
                    i.suspicious = True
                    i.save(update_fields=['suspicious'])

        return context


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
    paginate_by = 6
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
    comment = get_object_or_404(NewComment, pk=pk)
    obj = comment.content_type.get_object_for_this_type(pk=comment.object_id)
    if request.method == 'POST':
        if request.user == comment.author and (
                timezone.now() - comment.created < timezone.timedelta(minutes=10)) or request.user.is_superuser:
            form = NewCommentForm(request.POST, instance=comment)
        else:
            return HttpResponse('Ошибка доступа или время истекло')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            return redirect(obj.get_absolute_url())
        else:
            comment.delete()
            return redirect(obj.get_absolute_url())
    else:
        if request.user == comment.author and (
                timezone.now() - comment.created < timezone.timedelta(minutes=15)) or request.user.is_superuser:
            form = NewCommentForm(instance=comment)
        else:
            return HttpResponse('Ошибка доступа или время истекло')
    return render(request, 'core/post/edit_comment.html', {'comment_form': form})


# Удаление комментария
def delete_comment(request, pk):
    comment = get_object_or_404(NewComment, pk=pk)
    obj = comment.content_object
    if request.method == 'POST' and \
            ((request.user == comment.author and timezone.now() - comment.created < timezone.timedelta(
                minutes=10)) or request.user.is_superuser or request.user == obj.name):
        comment.delete()
        return redirect(obj.get_absolute_url())
    else:
        return HttpResponse('Ошибка доступа или время истекло')


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
    us = User.objects.filter(is_staff=True).order_by('id')
    a = []
    for i in us:
        print(i, len(i.get_user_permissions()))
        a.append([i, len(i.get_user_permissions())])
    a.sort(key=lambda x: x[1])
    queryset = [i[0] for i in a]
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
    paginate_by = 6
    template_name = 'core/tournaments/tournaments_list.html'


# Вьюха для поста и комментариев к нему.
# С одной стороны удобно одним методом, с другой-хезе как правильно надо)
"""
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
        """


# Учитывая, что потом пост-комменты будут использоваться для форума.. Такие дела
class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'core/post/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        post.views = post.views + 1
        post.save()
        comments_obj = NewComment.objects.filter(content_type=ContentType.objects.get_for_model(Post),
                                                 object_id=post.id,
                                                 parent=None)

        paginate = Paginator(comments_obj, 25)
        page = self.request.GET.get('page')

        try:
            comments = paginate.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            comments = paginate.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            comments = paginate.page(paginate.num_pages)

        context['page'] = page
        context['comments'] = comments
        comment_form = NewCommentForm()
        context['comment_form'] = comment_form
        return context


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
        comments_obj = NewComment.objects.filter(content_type=ContentType.objects.get_for_model(Profile),
                                                 object_id=prof.id,
                                                 parent=None)

        paginate = Paginator(comments_obj, 25)
        page = self.request.GET.get('page')

        try:
            comments = paginate.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            comments = paginate.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            comments = paginate.page(paginate.num_pages)

        context['page'] = page
        context['comments'] = comments
        comment_form = NewCommentForm()
        context['comment_form'] = comment_form
        return context


class AddCommentView(View):
    model = None

    def post(self, request, pk):
        obj = self.model.objects.get(id=pk)
        if request.method == 'POST':
            comment_form = NewCommentForm(data=request.POST)
            new_com = comment_form.save(commit=False)
            if request.POST.get("parent", None):
                new_com.parent_id = int(request.POST.get('parent'))
            new_com.object_id = obj.id
            new_com.author = request.user
            new_com.content_type = ContentType.objects.get_for_model(obj)
            new_com.save()
            return redirect(obj.get_absolute_url())


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
        author_profile = obj.author.user_profile
        # GenericForeignKey не поддерживает метод get_or_create
        try:
            likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id,
                                                  user=request.user)

            if likedislike.vote is not self.vote_type:

                if obj.author != request.user:
                    author_profile.karma -= likedislike.vote
                    author_profile.karma += self.vote_type
                    author_profile.save(update_fields=['karma'])

                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                # if obj.author != request.user:
                #    author_profile.karma -= likedislike.vote
                #    author_profile.save(update_fields=['karma'])
                likedislike.delete()
                result = False

        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
            if obj.author != request.user:
                obj.author.user_profile.karma += self.vote_type
                obj.author.user_profile.save(update_fields=['karma'])
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
