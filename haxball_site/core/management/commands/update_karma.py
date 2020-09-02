from core.models import Profile, Comment, Post
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        print('Обновляем карму всем пользователям')
        s = 0
        samo = 0
        a = Profile.objects.all()
        for profile in a:
            for comment in Comment.objects.filter(author=profile.name):
                s += comment.votes.sum_rating()
                samo += comment.votes.filter(user=profile.name, vote=1).count() - comment.votes.filter(user=profile.name,
                                                                                                       vote=-1).count()
            for post in Post.objects.filter(author=profile.name):
                s += post.votes.sum_rating()
                samo += post.votes.filter(user=profile.name, vote=1).count() - post.votes.filter(user=profile.name,
                                                                                                 vote=-1).count()
            print('{} установлена карма {}'.format(profile.name,profile.karma))
            profile.karma = s - samo
            profile.save(update_fields=['karma'])


