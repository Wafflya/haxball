from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from .models import Comment, Profile
from froala_editor.widgets import FroalaEditor


class CommentForm(forms.ModelForm):
    body = forms.CharField(label='Комментарий', widget=FroalaEditor)

    class Meta:
        model = Comment
        fields = ('body',)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about','born_date', 'avatar','city')

