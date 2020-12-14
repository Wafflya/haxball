from core.models import Profile, NewComment, Post, LikeDislike
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'The Zen of Python'

    def add_arguments(self, parser):
        parser.add_argument('user_names', nargs='+', type=str)


    def handle(self, *args, **options):
        print('Ставим дизлайки все комментам маса')

        try:
            user = User.objects.get(username=options['user_names'][0])
            user_from = User.objects.get(username=options['user_names'][1])
            vote = int(options['user_names'][2])
        except User.DoesNotExist:
           raise CommandError('Нет одного из пользователей')


        for comment in NewComment.objects.filter(author=user.id):
            from_marik = comment.votes.filter(user=user_from.id)
            #print(len(from_marik))
            if len(from_marik) == 1:
                ldl = from_marik[0]
                ldl.vote = vote
                ldl.save()
            else:
                dis = LikeDislike.objects.create(content_type=ContentType.objects.get_for_model(comment), object_id=comment.id, content_object=comment,
                                                 user=user_from, vote=vote)
                print('Создали ', dis)
            # for i in comment.votes.all():
            #   from_marik = i.
            #   print(i)
            #    print(i.user)
            # print(comment)
