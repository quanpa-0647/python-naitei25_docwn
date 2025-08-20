"""
Django management command to clear all seed data from the database
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db import connection
from django.core.management import call_command

from accounts.models import UserProfile
from novels.models import Author, Artist, Tag, Novel, Volume, Chapter, Chunk
from interactions.models import Comment, Review, Notification, Report

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear all seed data from the database (keeps superuser accounts)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )
        parser.add_argument(
            '--keep-admin',
            action='store_true',
            help='Keep admin accounts (default behavior)'
        )
        parser.add_argument(
            '--nuclear',
            action='store_true',
            help='Delete ALL data including admin accounts (dangerous!)'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete all seed data from the database!\n'
                    'This action cannot be undone.\n'
                )
            )
            if options['nuclear']:
                self.stdout.write(
                    self.style.ERROR(
                        'NUCLEAR MODE: This will delete ALL users including admins!\n'
                    )
                )
            
            confirm = input('Are you sure you want to continue? (type "yes" to confirm): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Operation cancelled.')
                return

        self.stdout.write(self.style.SUCCESS('Starting data cleanup...'))
        
        # Disable foreign key checks temporarily
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        try:
            with transaction.atomic():
                # Delete in order to respect foreign key constraints
                
                # Delete interactions first
                deleted_counts = {}
                
                deleted_counts['Reports'] = Report.objects.count()
                Report.objects.all().delete()
                
                deleted_counts['Notifications'] = Notification.objects.count()
                Notification.objects.all().delete()
                
                deleted_counts['Comments'] = Comment.objects.count()
                Comment.objects.all().delete()
                
                deleted_counts['Reviews'] = Review.objects.count()
                Review.objects.all().delete()
                
                # Delete novel-related data
                deleted_counts['Chunks'] = Chunk.objects.count()
                Chunk.objects.all().delete()
                
                deleted_counts['Chapters'] = Chapter.objects.count()
                Chapter.objects.all().delete()
                
                deleted_counts['Volumes'] = Volume.objects.count()
                Volume.objects.all().delete()
                
                deleted_counts['Novels'] = Novel.objects.count()
                Novel.objects.all().delete()
                
                deleted_counts['Tags'] = Tag.objects.count()
                Tag.objects.all().delete()
                
                deleted_counts['Artists'] = Artist.objects.count()
                Artist.objects.all().delete()
                
                deleted_counts['Authors'] = Author.objects.count()
                Author.objects.all().delete()
                
                # Delete users and profiles
                if options['nuclear']:
                    # Delete ALL users
                    deleted_counts['User Profiles'] = UserProfile.objects.count()
                    UserProfile.objects.all().delete()
                    
                    deleted_counts['Users'] = User.objects.count()
                    User.objects.all().delete()
                    
                    self.stdout.write(
                        self.style.ERROR('NUCLEAR MODE: Deleted ALL users including admins!')
                    )
                else:
                    # Keep superuser accounts but delete regular users
                    regular_users = User.objects.filter(is_superuser=False)
                    regular_profiles = UserProfile.objects.filter(user__is_superuser=False)
                    
                    deleted_counts['User Profiles'] = regular_profiles.count()
                    regular_profiles.delete()
                    
                    deleted_counts['Regular Users'] = regular_users.count()
                    regular_users.delete()
                    
                    self.stdout.write(
                        self.style.SUCCESS('Kept admin/superuser accounts')
                    )
        
        finally:
            # Re-enable foreign key checks
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")        # Display deletion summary
        self.stdout.write(self.style.SUCCESS('\nDeletion Summary:'))
        for model_name, count in deleted_counts.items():
            if count > 0:
                self.stdout.write(f"  {model_name}: {count} deleted")
        
        # Reset auto-increment counters
        self.stdout.write('\nResetting database sequences...')
        try:
            call_command('sqlsequencereset', 'novels', 'accounts', 'interactions', verbosity=0)
            self.stdout.write(self.style.SUCCESS('Database sequences reset'))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not reset sequences: {e}')
            )
        
        self.stdout.write(self.style.SUCCESS('\nData cleanup completed successfully!'))
