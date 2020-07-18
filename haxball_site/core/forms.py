from django import forms
from .models import Comment, Profile


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about','born_date', 'avatar')