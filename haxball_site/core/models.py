import collections

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum, Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


# Менеджер модели лайк-дизлайк
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

    def comments(self):
        return self.get_queryset().filter(content_type__model='comment').order_by('-comments__pub_date')


# Модель для лайк-дизлайк системы
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

    class Meta:
        verbose_name = 'Лайк/дизлайк голос'
        verbose_name_plural = "Лайк/дизлайк голоса"


# Огромный раздел форума в котором категории создаются админами
class Themes(models.Model):
    title = models.CharField('Тема', max_length=256)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Раздел форума'
        verbose_name_plural = "Разделы форума"


# Модель для категории поста(Новость, Фасткап, Регламент, Турнир, Трансляция, Архив, общение...)
# Это также секции форума, в которых можно публиковать посты, поэтому доступно описание, если тема
# неофицальная, ставим ис-оффишл НОУ и пишем описание, привязываем к теме форума
class Category(models.Model):
    title = models.CharField('Категория', max_length=256)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField('Описание категории', blank=True)
    is_official = models.BooleanField(default=True, verbose_name = 'Официальная')
    theme = models.ForeignKey(Themes, verbose_name='Тема на форуме', on_delete=models.CASCADE, blank=True, null=True,
                              related_name='category_in_theme')
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:forum_category', args=[self.slug])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Модель для поста
class Post(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    category = models.ForeignKey(Category, verbose_name='Категория поста', on_delete=models.SET_NULL, blank=True,
                                 null=True, related_name='posts_in_category')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='blog_posts')
    slug = models.SlugField(max_length=250)
    body = models.TextField("Текст поста")
    publish = models.DateTimeField('Начало публикации', default=timezone.now)
    created = models.DateTimeField("Опубликовано", auto_now_add=True)
    updated = models.DateTimeField("Изменено", auto_now=True)
    important = models.BooleanField("Закрепленный пост", default=False)
    votes = GenericRelation(LikeDislike, related_query_name='posts')
    views = models.PositiveIntegerField(default=0)
    commentable = models.BooleanField("Комментируемая запись", default=True)

    def get_absolute_url(self):
        return reverse('core:post_detail', args=[self.id, self.slug])

    def last_comment(self):
        return self.comments.annotate(Max('created'))

    def __str__(self):
        return 'Пост: {}'.format(self.title)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


# Модель для комментария
class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Место', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Автор', related_name='comments_by_user', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', verbose_name='Родитель', on_delete=models.SET_NULL, blank=True, null=True,
                               related_name="childs")
    votes = GenericRelation(LikeDislike, related_query_name='comments')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return 'Комментарий от {} к {}'.format(self.author, self.post.title)

    def is_parent(self):
        return self.parent == None

    def has_childs(self):
        return self.childs.count() > 0

    def all_childs(self):
        return sorted(list(bfs(self)), key=lambda x: x.created)

    def childs_count(self):
        return len(list(bfs(self)))


# Обход графа в ширину хе-хе, хоть где-то пригодилось)
def bfs(root):
    visited = set()
    queue = collections.deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in vertex.childs.all():
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return visited

    # Модель для профиля пользователя


class Profile(models.Model):
    name = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                                related_name='user_profile')
    slug = AutoSlugField(populate_from='name')
    avatar = models.ImageField('Аватар', upload_to='users_avatars/', default='users_avatars/default/default.png')
    background = models.ImageField('Фон профиля', upload_to='users_background/', blank=True, null=True)
    born_date = models.DateField('Дата рождения', blank=True, null=True)
    about = models.TextField(max_length=1000, blank=True)
    city = models.CharField(max_length=100, blank=True)
    vk = models.CharField(max_length=100, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    discord = models.CharField(max_length=100, blank=True)
    views = models.PositiveIntegerField(default=0)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(name=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.user_profile.save()

    def get_absolute_url(self):
        return reverse('core:profile_detail', args=[self.id, self.slug])

    def __str__(self):
        return self.name.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class UserIcon(models.Model):
    title = models.CharField('Название', max_length=256)
    description = models.CharField('Описание(при наведении)', max_length=100, blank=True)
    image = models.ImageField('Иконка', upload_to='user_icon/', blank=True, null=True)
    user = models.ManyToManyField(Profile, related_name='user_icon', blank=True, null=True)

    class Meta:
        verbose_name = 'Иконка'
        verbose_name_plural = 'Иконки'

