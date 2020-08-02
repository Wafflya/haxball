from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from markdownx.fields import MarkdownxFormField

from .models import Comment, Profile, Post
from froala_editor.widgets import FroalaEditor
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField


class CommentForm(forms.ModelForm):
    #body = SummernoteTextFormField()
    body = forms.CharField(widget=FroalaEditor(theme='dark'))

    class Meta:
        model = Comment
        fields = ('body',)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about','born_date', 'avatar','city')


class PostForm(forms.ModelForm):

    body = forms.CharField(label='Пост', widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Post
        fields = ('title', 'body')

