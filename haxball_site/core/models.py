from datetime import date

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone


#Менеджер модели лайк-дизлайк
class LikeDislikeManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        # Забираем queryset с записями больше 0
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        # Забираем queryset с записями меньше 0
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        # Забираем суммарный рейтинг
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0

    def posts(self):
        return self.get_queryset().filter(content_type__model='post').order_by('-posts__pub_date')


#Модель для лайк-дизлайк системы
class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Не нравится'),
        (LIKE, 'Нравится')
    )

    vote = models.SmallIntegerField(verbose_name="Голос", choices=VOTES)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()

# Модель для комментария
class Comment(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор', related_name='comments_by_user', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', verbose_name='Родитель', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return 'Комментарий от {}'.format(self.author)


#Модель для поста
class Post(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='blog_posts')
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField("Текст поста")
    publish = models.DateTimeField('Начало публикации', default=timezone.now)
    created = models.DateTimeField("Опубликовано", auto_now_add=True)
    updated = models.DateTimeField("Изменено", auto_now=True)
    important = models.BooleanField(default=False)
    comments = models.ManyToManyField(Comment, related_name='post_comments', blank=True)
    votes = GenericRelation(LikeDislike, related_query_name='posts')



    def get_absolute_url(self):
        return reverse('core:post_detail', args=[self.id, self.slug])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


# Модель для профиля пользователя
class Profile(models.Model):
    name = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                                related_name='user_profile')
    slug = AutoSlugField(populate_from='name')
    avatar = models.ImageField('Аватар', upload_to='users_avatars/', blank=True)
    born_date = models.DateField('Дата рождения', blank=True, null=True)
    about = models.TextField(max_length=1000, blank=True)
    comments = models.ManyToManyField(Comment, related_name='profile_comments', blank=True)

    def get_absolute_url(self):
        return reverse('core:profile_detail', args=[self.id, self.slug])

    def __str__(self):
        return self.name.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'





