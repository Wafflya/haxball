from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.exceptions import PermissionDenied
from django_summernote.fields import SummernoteTextFormField
from django import forms
from django.contrib import admin

from .models import *


# Register your models here.


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(label='Пост', widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Post
        fields = '__all__'


class CommentAdminForm(forms.ModelForm):
    body = SummernoteTextFormField(label='Комментарий')

    class Meta:
        model = Comment
        fields = '__all__'




"""
def delete_selected(modeladmin, request, queryset):
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    if request.POST.get('post'):
        for obj in queryset:
            obj.delete()
    else:
        return delete_selected(modeladmin, request, queryset)
delete_selected.short_description = "Delete selected objects"
"""


@admin.register(LikeDislike)
class LikeDisLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'vote', 'user', 'content_type', 'object_id', 'content_object')
    list_filter = ('user',)
    list_display_links = ('id',)
    list_editable = ('vote',)


class CommentInline(admin.StackedInline):
    model = Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'views', 'category', 'created', 'updated', 'important')
    list_filter = ('created', 'author')
    search_fields = ('title', 'body')
    # slug = AutoSlugField(populate_from='title', unique_for_date='publish')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    form = PostAdminForm
    # inlines = [CommentInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'background', 'karma')
    list_filter = ('id', 'name')
    list_display_links = ('name',)
    readonly_fields = ('karma',)


@admin.register(Themes)
class ThemesAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(UserIcon)
class UserIconAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    filter_horizontal = ('user',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description', 'is_official', 'theme')
    prepopulated_fields = {'slug': ('title',)}

"""
# Старые комменты
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created', 'body',)
    list_filter = ('created', 'author')
    search_fields = ('body',)
    form = CommentAdminForm
"""

@admin.register(NewComment)
class NewCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'parent', 'created', 'body', 'content_type', 'object_id', 'content_object')
    list_filter = ('created', 'author')
    search_fields = ('body',)
    form = CommentAdminForm


@admin.register(IPAdress)
class IPAdressAdmin(admin.ModelAdmin):
    list_display = ('ip', 'name', 'created', 'update', 'suspicious')
    list_filter = ('ip', 'name')
