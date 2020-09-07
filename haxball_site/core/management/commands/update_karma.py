from core.models import Profile, NewComment, Post
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        print('Обновляем карму всем пользователям')
        a = Profile.objects.all()
        for profile in a:
            s = 0
            samo = 0
            for comment in NewComment.objects.filter(author=profile.name):
                s += comment.votes.sum_rating()
                samo += comment.votes.filter(user=profile.name, vote=1).count() - comment.votes.filter(user=profile.name,
                                                                                                       vote=-1).count()
            for post in Post.objects.filter(author=profile.name):
                s += post.votes.sum_rating()
                samo += post.votes.filter(user=profile.name, vote=1).count() - post.votes.filter(user=profile.name,
                                                                                                 vote=-1).count()
            profile.karma = s - samo
            profile.save(update_fields=['karma'])
            print('{} установлена карма {}'.format(profile.name,profile.karma))


