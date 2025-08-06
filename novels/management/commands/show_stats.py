from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Sum
from accounts.models import User, UserProfile
from novels.models import (
    Author, Artist, Tag, Novel, NovelTag, Volume, Chapter, Chunk,
    ReadingHistory, Favorite
)
from interactions.models import Comment, Review, Notification, Report
from constants import ProgressStatus, ApprovalStatus, UserRole


class Command(BaseCommand):
    help = 'Show database statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('DATABASE STATISTICS'))
        self.stdout.write('=' * 50)
        
        # Users Statistics
        self.show_user_stats()
        self.stdout.write('')
        
        # Content Statistics
        self.show_content_stats()
        self.stdout.write('')
        
        # Novel Statistics
        self.show_novel_stats()
        self.stdout.write('')
        
        # Interaction Statistics
        self.show_interaction_stats()

    def show_user_stats(self):
        self.stdout.write(self.style.HTTP_INFO('USERS'))
        self.stdout.write('-' * 20)
        
        total_users = User.objects.count()
        self.stdout.write(f'Total Users: {total_users}')
        
        # Users by role
        for role in UserRole:
            count = User.objects.filter(role=role.value).count()
            self.stdout.write(f'  {role.name}: {count}')
        
        # User status
        active_users = User.objects.filter(is_active=True).count()
        blocked_users = User.objects.filter(is_blocked=True).count()
        verified_users = User.objects.filter(is_email_verified=True).count()
        
        self.stdout.write(f'Active Users: {active_users}')
        self.stdout.write(f'Blocked Users: {blocked_users}')
        self.stdout.write(f'Verified Users: {verified_users}')

    def show_content_stats(self):
        self.stdout.write(self.style.HTTP_INFO('CONTENT'))
        self.stdout.write('-' * 20)
        
        self.stdout.write(f'Authors: {Author.objects.count()}')
        self.stdout.write(f'Artists: {Artist.objects.count()}')
        self.stdout.write(f'Tags: {Tag.objects.count()}')
        self.stdout.write(f'Volumes: {Volume.objects.count()}')
        self.stdout.write(f'Chapters: {Chapter.objects.count()}')
        self.stdout.write(f'Chunks: {Chunk.objects.count()}')
        
        # Chapter approval status
        approved_chapters = Chapter.objects.filter(approved=True).count()
        total_chapters = Chapter.objects.count()
        self.stdout.write(f'Approved Chapters: {approved_chapters}/{total_chapters}')

    def show_novel_stats(self):
        self.stdout.write(self.style.HTTP_INFO('NOVELS'))
        self.stdout.write('-' * 20)
        
        total_novels = Novel.objects.count()
        self.stdout.write(f'Total Novels: {total_novels}')
        
        # Novels by progress status
        for status in ProgressStatus:
            count = Novel.objects.filter(progress_status=status.value).count()
            self.stdout.write(f'  {status.name}: {count}')
        
        # Novels by approval status
        self.stdout.write('\\nApproval Status:')
        for status in ApprovalStatus:
            count = Novel.objects.filter(approval_status=status.value).count()
            self.stdout.write(f'  {status.name}: {count}')
        
        # Novel statistics
        stats = Novel.objects.aggregate(
            avg_rating=Avg('rating_avg'),
            total_views=Sum('view_count'),
            total_favorites=Sum('favorite_count'),
            total_words=Sum('word_count')
        )
        
        self.stdout.write('\\nNovel Metrics:')
        self.stdout.write(f"  Average Rating: {stats['avg_rating']:.2f}" if stats['avg_rating'] else "  Average Rating: 0.00")
        self.stdout.write(f"  Total Views: {stats['total_views']:,}" if stats['total_views'] else "  Total Views: 0")
        self.stdout.write(f"  Total Favorites: {stats['total_favorites']:,}" if stats['total_favorites'] else "  Total Favorites: 0")
        self.stdout.write(f"  Total Words: {stats['total_words']:,}" if stats['total_words'] else "  Total Words: 0")

    def show_interaction_stats(self):
        self.stdout.write(self.style.HTTP_INFO('INTERACTIONS'))
        self.stdout.write('-' * 20)
        
        self.stdout.write(f'Comments: {Comment.objects.count()}')
        self.stdout.write(f'Reviews: {Review.objects.count()}')
        self.stdout.write(f'Favorites: {Favorite.objects.count()}')
        self.stdout.write(f'Reading History: {ReadingHistory.objects.count()}')
        self.stdout.write(f'Notifications: {Notification.objects.count()}')
        self.stdout.write(f'Reports: {Report.objects.count()}')
        
        # Comment replies
        replies = Comment.objects.filter(parent_comment__isnull=False).count()
        self.stdout.write(f'Comment Replies: {replies}')
        
        # Reported content
        reported_comments = Comment.objects.filter(is_reported=True).count()
        self.stdout.write(f'Reported Comments: {reported_comments}')
        
        # Notification status
        read_notifications = Notification.objects.filter(is_read=True).count()
        total_notifications = Notification.objects.count()
        self.stdout.write(f'Read Notifications: {read_notifications}/{total_notifications}')
        
        # Most active users
        self.stdout.write('\\nTop 5 Most Active Users:')
        top_commenters = User.objects.annotate(
            comment_count=Count('comment')
        ).order_by('-comment_count')[:5]
        
        for i, user in enumerate(top_commenters, 1):
            self.stdout.write(f'  {i}. {user.username}: {user.comment_count} comments')

    def format_number(self, num):
        """Format large numbers with commas"""
        if num is None:
            return "0"
        return f"{num:,}"
