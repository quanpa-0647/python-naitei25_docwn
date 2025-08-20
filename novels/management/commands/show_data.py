"""
Django management command to display database statistics and sample data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg

from accounts.models import UserProfile
from novels.models import Author, Artist, Tag, Novel, Volume, Chapter, Chunk
from interactions.models import Comment, Review, Notification, Report

User = get_user_model()


class Command(BaseCommand):
    help = 'Display comprehensive database statistics and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics and sample records'
        )
        parser.add_argument(
            '--samples',
            type=int,
            default=5,
            help='Number of sample records to show (default: 5)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Database Statistics Report'))
        self.stdout.write('=' * 50)
        
        # Basic counts
        self.show_basic_counts()
        
        # User statistics
        self.show_user_statistics()
        
        # Novel statistics
        self.show_novel_statistics()
        
        # Interaction statistics
        self.show_interaction_statistics()
        
        if options['detailed']:
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.SUCCESS('Sample Data'))
            self.stdout.write('=' * 50)
            self.show_sample_data(options['samples'])

    def show_basic_counts(self):
        """Display basic record counts"""
        self.stdout.write(f"\n{self.style.HTTP_INFO('Record Counts:')}")
        
        counts = {
            'Users': User.objects.count(),
            'User Profiles': UserProfile.objects.count(),
            'Authors': Author.objects.count(),
            'Artists': Artist.objects.count(),
            'Tags': Tag.objects.count(),
            'Novels': Novel.objects.count(),
            'Volumes': Volume.objects.count(),
            'Chapters': Chapter.objects.count(),
            'Chunks': Chunk.objects.count(),
            'Comments': Comment.objects.count(),
            'Reviews': Review.objects.count(),
            'Notifications': Notification.objects.count(),
            'Reports': Report.objects.count(),
        }
        
        for name, count in counts.items():
            self.stdout.write(f"  {name}: {count}")

    def show_user_statistics(self):
        """Display user-related statistics"""
        self.stdout.write(f"\n{self.style.HTTP_INFO('User Statistics:')}")
        
        total_users = User.objects.count()
        if total_users == 0:
            self.stdout.write("  No users found")
            return
        
        active_users = User.objects.filter(is_active=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        users_with_profiles = User.objects.filter(profile__isnull=False).count()
        
        self.stdout.write(f"  Total Users: {total_users}")
        self.stdout.write(f"  Active Users: {active_users}")
        self.stdout.write(f"  Superusers: {superusers}")
        self.stdout.write(f"  Users with Profiles: {users_with_profiles}")
        
        # User role distribution
        role_distribution = User.objects.values('role').annotate(count=Count('role'))
        if role_distribution:
            self.stdout.write("  Role Distribution:")
            for role_data in role_distribution:
                role = role_data['role'] or 'None'
                count = role_data['count']
                self.stdout.write(f"    {role}: {count}")

    def show_novel_statistics(self):
        """Display novel-related statistics"""
        self.stdout.write(f"\n{self.style.HTTP_INFO('Novel Statistics:')}")
        
        total_novels = Novel.objects.count()
        if total_novels == 0:
            self.stdout.write("  No novels found")
            return
        
        # Basic novel stats
        approved_novels = Novel.objects.filter(approval_status='a').count()
        anonymous_novels = Novel.objects.filter(is_anonymous=True).count()
        
        self.stdout.write(f"  Total Novels: {total_novels}")
        self.stdout.write(f"  Approved Novels: {approved_novels}")
        self.stdout.write(f"  Anonymous Novels: {anonymous_novels}")
        
        # Progress status distribution
        progress_distribution = Novel.objects.values('progress_status').annotate(count=Count('progress_status'))
        if progress_distribution:
            self.stdout.write("  Progress Status Distribution:")
            for status_data in progress_distribution:
                status = status_data['progress_status'] or 'None'
                count = status_data['count']
                self.stdout.write(f"    {status}: {count}")
        
        # Volume and chapter statistics
        total_volumes = Volume.objects.count()
        total_chapters = Chapter.objects.count()
        total_chunks = Chunk.objects.count()
        
        self.stdout.write(f"  Total Volumes: {total_volumes}")
        self.stdout.write(f"  Total Chapters: {total_chapters}")
        self.stdout.write(f"  Total Chunks: {total_chunks}")
        
        if total_novels > 0:
            avg_volumes_per_novel = total_volumes / total_novels
            self.stdout.write(f"  Average Volumes per Novel: {avg_volumes_per_novel:.2f}")
        
        if total_volumes > 0:
            avg_chapters_per_volume = total_chapters / total_volumes
            self.stdout.write(f"  Average Chapters per Volume: {avg_chapters_per_volume:.2f}")
        
        # Tag usage
        total_tags = Tag.objects.count()
        self.stdout.write(f"  Total Tags: {total_tags}")
        
        # Most popular tags
        popular_tags = Tag.objects.annotate(
            novel_count=Count('novels')
        ).order_by('-novel_count')[:5]
        
        if popular_tags:
            self.stdout.write("  Most Popular Tags:")
            for tag in popular_tags:
                self.stdout.write(f"    {tag.name}: {tag.novel_count} novels")

    def show_interaction_statistics(self):
        """Display interaction-related statistics"""
        self.stdout.write(f"\n{self.style.HTTP_INFO('Interaction Statistics:')}")
        
        total_comments = Comment.objects.count()
        total_reviews = Review.objects.count()
        
        self.stdout.write(f"  Total Comments: {total_comments}")
        self.stdout.write(f"  Total Reviews: {total_reviews}")
        
        if total_comments > 0:
            # Comment statistics
            parent_comments = Comment.objects.filter(parent_comment=None).count()
            reply_comments = Comment.objects.filter(parent_comment__isnull=False).count()
            
            self.stdout.write(f"  Parent Comments: {parent_comments}")
            self.stdout.write(f"  Reply Comments: {reply_comments}")
            
            # Average likes per comment
            avg_likes = Comment.objects.aggregate(avg_likes=Avg('like_count'))['avg_likes']
            if avg_likes:
                self.stdout.write(f"  Average Likes per Comment: {avg_likes:.2f}")
        
        if total_reviews > 0:
            # Review statistics
            avg_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
            if avg_rating:
                self.stdout.write(f"  Average Review Rating: {avg_rating:.2f}")
            
            # Rating distribution
            rating_distribution = Review.objects.values('rating').annotate(count=Count('rating')).order_by('rating')
            if rating_distribution:
                self.stdout.write("  Rating Distribution:")
                for rating_data in rating_distribution:
                    rating = rating_data['rating']
                    count = rating_data['count']
                    self.stdout.write(f"    {rating} stars: {count} reviews")

    def show_sample_data(self, sample_count):
        """Display sample records from each model"""
        
        # Sample users
        users = User.objects.select_related('profile')[:sample_count]
        if users:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Users:')}")
            for user in users:
                profile_info = ""
                if hasattr(user, 'profile') and user.profile:
                    profile_info = f" ({user.profile.display_name})"
                self.stdout.write(f"  {user.username} - {user.email}{profile_info}")
        
        # Sample authors
        authors = Author.objects.all()[:sample_count]
        if authors:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Authors:')}")
            for author in authors:
                pen_name = f" (pen: {author.pen_name})" if author.pen_name else ""
                self.stdout.write(f"  {author.name}{pen_name}")
        
        # Sample novels
        novels = Novel.objects.select_related('author').prefetch_related('tags')[:sample_count]
        if novels:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Novels:')}")
            for novel in novels:
                author_name = novel.author.name if novel.author else "Unknown"
                tag_names = ", ".join([tag.name for tag in novel.tags.all()[:3]])
                tag_info = f" [Tags: {tag_names}]" if tag_names else ""
                self.stdout.write(f"  '{novel.name}' by {author_name}{tag_info}")
        
        # Sample chapters
        chapters = Chapter.objects.select_related('volume__novel')[:sample_count]
        if chapters:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Chapters:')}")
            for chapter in chapters:
                novel_name = chapter.volume.novel.name
                self.stdout.write(f"  '{chapter.title}' from '{novel_name}'")
        
        # Sample comments
        comments = Comment.objects.select_related('user', 'novel')[:sample_count]
        if comments:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Comments:')}")
            for comment in comments:
                user_name = comment.user.username if comment.user else "Anonymous"
                novel_name = comment.novel.name
                content_preview = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
                self.stdout.write(f"  {user_name} on '{novel_name}': {content_preview}")
        
        # Sample reviews
        reviews = Review.objects.select_related('user', 'novel')[:sample_count]
        if reviews:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Sample Reviews:')}")
            for review in reviews:
                user_name = review.user.username
                novel_name = review.novel.name
                self.stdout.write(f"  {user_name} rated '{novel_name}': {review.rating}/5 stars")
