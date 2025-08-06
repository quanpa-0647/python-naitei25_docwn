from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, UserProfile
from novels.models import (
    Author, Artist, Tag, Novel, NovelTag, Volume, Chapter, Chunk,
    ReadingHistory, Favorite
)
from interactions.models import Comment, Review, Notification, Report


class Command(BaseCommand):
    help = 'Clear all test data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from the database.\\n'
                    'Use --confirm flag to proceed: python manage.py clear_test_data --confirm'
                )
            )
            return

        self.stdout.write('Clearing all data from database...')
        
        with transaction.atomic():
            # Delete in reverse order of dependencies
            models_to_clear = [
                (Report, 'Reports'),
                (Notification, 'Notifications'),
                (Comment, 'Comments'),
                (Review, 'Reviews'),
                (ReadingHistory, 'Reading History'),
                (Favorite, 'Favorites'),
                (Chunk, 'Chunks'),
                (Chapter, 'Chapters'),
                (Volume, 'Volumes'),
                (NovelTag, 'Novel Tags'),
                (Novel, 'Novels'),
                (Tag, 'Tags'),
                (Artist, 'Artists'),
                (Author, 'Authors'),
                (UserProfile, 'User Profiles'),
                (User, 'Users'),
            ]
            
            total_deleted = 0
            for model, name in models_to_clear:
                count = model.objects.count()
                model.objects.all().delete()
                total_deleted += count
                self.stdout.write(f'Cleared {count} {name}')
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleared {total_deleted} records from database'
            )
        )
