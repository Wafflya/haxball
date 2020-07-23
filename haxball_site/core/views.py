
import json
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.list import MultipleObjectMixin

from .forms import CommentForm, EditProfileForm
from .models import Post, Profile, LikeDislike


# Вьюха для списка постов

class PostListView(ListView):
    queryset = Post.objects.all().order_by('-important', '-created', )
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'core/post/list.html'


# Вьюха для поста

def post_detail(request, slug, id):
    post = get_object_or_404(Post, slug=slug,
                             id=id)

    # List of active comments for this post

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.save()
            post.comments.add(new_comment)
    else:
        comment_form = CommentForm()

    comments_obj = post.comments.all()
    paginat = Paginator(comments_obj, 2)
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
        comment_list = self.object.comments.all()
        paginat = Paginator(comment_list, 2)
        page = self.request.GET.get("page")
        try:
            comment_list = paginat.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            comment_list = paginat.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            comment_list = paginat.page(paginat.num_pages)

        context = super(ProfileDetail, self).get_context_data(comments_in_profile=comment_list, page=page, **kwargs)
        print(context)

        return context


class AddComment(ListView, View):

    def post(self, request, id, slug):
        comment_form = CommentForm(request.POST)

        if Profile.objects.filter(id=id, slug=slug).exists():
            object_to = Profile.objects.get(id=id, slug=slug)
        else:
            object_to = Post.objects.get(id=id, slug=slug)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.save()
            object_to.comments.add(new_comment)

        return redirect(object_to.get_absolute_url())


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
