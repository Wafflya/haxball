from core.models import Profile, Comment, Post
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q, Count

from ...models import Comment, NewComment, LikeDislike


class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        """
        all_old = Comment.objects.all().exclude(Q(childs = None) & ~Q(parent=None)).order_by('created')
        added = []
        print(all_old)
        for com in all_old:
            post = com.post
            print(post)
            if com not in added:
                if com.parent == None:
                    #NewComment.objects.create(content_type=ContentType.objects.get_for_model(Post), object_id=post.id)
                    print(com.id, com, com.created)
                    added.append(com)
            # if com.has_childs():
            for child in com.childs.all():
                print(child.id, child, child.parent)
                # NewComment.objects.create(content_type=ContentType.objects.get_for_model(Post),
                # object_id=post.id, parent=com)
                added.append(child)
            for ldl in com.votes.all():
                print(ldl)
        """
        all_com = list(Comment.objects.all())
        new_com = []
        for com in all_com:
            post = com.post
            nc = NewComment.objects.create(content_type=ContentType.objects.get_for_model(Post),
                                           object_id=post.id, author=com.author, body=com.body, created=com.created,
                                           parent=None)
            for ldl in com.votes.all():
                ldl.content_type = ContentType.objects.get_for_model(NewComment)
                ldl.object_id = nc.id
                ldl.save()
            print(nc)
            new_com.append(nc)

        for i, com in enumerate(all_com):
            if com.has_childs():
                for child in com.childs.all():
                    print(all_com.index(child))
                    new_com[all_com.index(child)].parent = new_com[i]
                    new_com[all_com.index(child)].save(update_fields=['parent'])