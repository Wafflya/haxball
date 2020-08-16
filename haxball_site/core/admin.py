from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from .models import *


# Register your models here.


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(label='Пост', widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Post
        fields = '__all__'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views', 'category', 'created', 'important')
    list_filter = ('created', 'publish', 'author')
    search_fields = ('title', 'body')
    #slug = AutoSlugField(populate_from='title', unique_for_date='publish')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    form = PostAdminForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_filter = ('id', 'name')

@admin.register(Themes)
class ThemesAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(UserIcon)
class UserIconAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description', 'is_official', 'theme')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','author', 'created', 'body', )


@admin.register(LikeDislike)
class LikeDisLike(admin.ModelAdmin):
    list_display = ('vote', 'user', 'content_type', 'object_id', 'content_object')
