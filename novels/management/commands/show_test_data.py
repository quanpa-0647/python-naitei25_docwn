from django.core.management.base import BaseCommand
from accounts.models import User
from novels.models import Novel, Chapter
from interactions.models import Comment, Review


class Command(BaseCommand):
    help = 'Show example test data for testing purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('SAMPLE TEST DATA FOR TESTING'))
        self.stdout.write('=' * 50)
        
        # Sample Users
        self.stdout.write('\\nSAMPLE USERS:')
        users = User.objects.all()[:5]
        for user in users:
            self.stdout.write(f'- Email: {user.email} | Username: {user.username} | Role: {user.role}')
        
        # Sample Novels
        self.stdout.write('\\nSAMPLE NOVELS:')
        novels = Novel.objects.all()[:5]
        for novel in novels:
            self.stdout.write(f'- {novel.name} by {novel.author.name if novel.author else "Unknown"}')
            self.stdout.write(f'  Status: {novel.approval_status} | Progress: {novel.progress_status}')
            self.stdout.write(f'  Rating: {novel.rating_avg}/5 | Views: {novel.view_count:,}')
        
        # Sample Chapters
        self.stdout.write('\\nSAMPLE CHAPTERS:')
        chapters = Chapter.objects.filter(approved=True)[:5]
        for chapter in chapters:
            self.stdout.write(f'- {chapter.novel.name} - {chapter.title}')
            self.stdout.write(f'  Word count: {chapter.word_count} | Views: {chapter.view_count}')
        
        # Sample Comments
        self.stdout.write('\\nSAMPLE COMMENTS:')
        comments = Comment.objects.all()[:5]
        for comment in comments:
            self.stdout.write(f'- {comment.user.username} on "{comment.novel.name}":')
            self.stdout.write(f'  "{comment.content[:80]}..." | Likes: {comment.like_count}')
        
        # Sample Reviews
        self.stdout.write('\\nSAMPLE REVIEWS:')
        reviews = Review.objects.all()[:5]
        for review in reviews:
            self.stdout.write(f'- {review.user.username} rated "{review.novel.name}": {review.rating}/5')
            self.stdout.write(f'  "{review.content[:80]}..."')
        
        # Login Credentials
        self.stdout.write('\\n' + '=' * 50)
        self.stdout.write(self.style.WARNING('TEST LOGIN CREDENTIALS:'))
        self.stdout.write('Admin User:')
        self.stdout.write('  Email: testadmin@docwn.com')
        self.stdout.write('  Username: testadmin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('')
        self.stdout.write('Regular Users:')
        self.stdout.write('  Email: user1@test.com | Username: testuser1 | Password: password123')
        self.stdout.write('  Email: user2@test.com | Username: testuser2 | Password: password123')
        self.stdout.write('  Email: testuser1000@example.com | Username: testuser1000 | Password: password123')
        
        self.stdout.write('\\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('Your database now has comprehensive test data!'))
        self.stdout.write('')
        self.stdout.write('Features you can now test:')
        self.stdout.write('✓ User registration and login (different roles)')
        self.stdout.write('✓ Novel browsing and reading')
        self.stdout.write('✓ Search and filtering')
        self.stdout.write('✓ Comments and reviews')
        self.stdout.write('✓ Reading history tracking')
        self.stdout.write('✓ Favorites system')
        self.stdout.write('✓ Notifications')
        self.stdout.write('✓ Content reporting')
        self.stdout.write('✓ Admin panel features')
        self.stdout.write('✓ Novel creation and management')
        self.stdout.write('✓ Chapter reading')
        self.stdout.write('✓ User profiles and interactions')
