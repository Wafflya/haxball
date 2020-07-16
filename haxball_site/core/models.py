from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Post(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='blog_posts')
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField("Текст поста")
    publish = models.DateTimeField('Начало публикации', default=timezone.now)
    created = models.DateTimeField("Опубликовано", auto_now_add=True)
    updated = models.DateTimeField("Изменено", auto_now=True)
    important = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('core:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Profile(models.Model):
    name = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='user_profile')
    slug = AutoSlugField(populate_from='name')
    avatar = models.ImageField('Аватар', upload_to='users_avatars/', blank=True)
    about = models.TextField()

    def get_absolute_url(self):
        return reverse('core:profile_detail', args=[self.slug])

    def __str__(self):
        return self.name.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Автор', related_name='comments_by_user', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created',)

    def __str__(self):
        return 'Комментарий от {} к записи {}'.format(self.author, self.post)