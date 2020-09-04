from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django_summernote.fields import SummernoteTextFormField

from .models import Comment, Profile, Post, NewComment


class NewCommentForm(forms.ModelForm):
    body = SummernoteTextFormField()

    # body = forms.CharField(widget=FroalaEditor(theme='dark'))

    class Meta:
        model = NewComment
        fields = ('body',)


class CommentForm(forms.ModelForm):
    body = SummernoteTextFormField()

    # body = forms.CharField(widget=FroalaEditor(theme='dark'))

    class Meta:
        model = Comment
        fields = ('body',)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about', 'born_date', 'avatar', 'city', 'vk', 'discord', 'telegram')


class PostForm(forms.ModelForm):
    body = forms.CharField(label='Пост', widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Post
        fields = ('title', 'body')
