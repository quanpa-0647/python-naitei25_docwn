import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker
from accounts.models import User, UserProfile
from novels.models import (
    Author, Artist, Tag, Novel, NovelTag, Volume, Chapter, Chunk,
    ReadingHistory, Favorite
)
from interactions.models import Comment, Review, Notification, Report
from constants import (
    Gender, ProgressStatus, ApprovalStatus, UserRole
)

fake = Faker(['vi_VN', 'en_US'])


class Command(BaseCommand):
    help = 'Generate a smaller, focused dataset for quick testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating quick test dataset...')
        
        # First, clean up any bad data
        self.cleanup_bad_data()
        
        with transaction.atomic():
            # Create essential users
            admin = self.create_admin_user()
            users = self.create_sample_users()
            all_users = [admin] + users
            
            # Create core content
            authors = self.create_sample_authors()
            artists = self.create_sample_artists()
            tags = self.create_sample_tags()
            novels = self.create_sample_novels(all_users, authors, artists, tags)
            
            # Create content structure
            volumes = self.create_sample_volumes(novels)
            chapters = self.create_sample_chapters(volumes)
            chunks = self.create_sample_chunks(chapters)
            
            # Create interactions
            self.create_sample_interactions(all_users, novels, chapters)
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Quick test dataset created:\\n'
                f'- 1 admin + {len(users)} users\\n'
                f'- {len(authors)} authors, {len(artists)} artists\\n'
                f'- {len(tags)} tags\\n'
                f'- {len(novels)} novels\\n'
                f'- {len(volumes)} volumes, {len(chapters)} chapters\\n'
                f'- Interactions: favorites, comments, reviews, reading history'
            )
        )

    def cleanup_bad_data(self):
        """Clean up any existing bad data"""
        from novels.models import Novel, Volume, Chapter
        
        # Fix novels without slugs
        novels_without_slugs = Novel.objects.filter(slug__isnull=True) | Novel.objects.filter(slug='')
        for novel in novels_without_slugs:
            novel.slug = f'novel-{novel.id}'
            novel.save(update_fields=['slug'])
            self.stdout.write(f'Fixed novel slug: {novel.name}')
        
        # Fix volumes with invalid novel relationships
        invalid_volumes = Volume.objects.filter(novel__isnull=True)
        for volume in invalid_volumes:
            self.stdout.write(f'Removing invalid volume: {volume.id}')
            volume.delete()
        
        # Fix chapters with invalid volume relationships
        invalid_chapters = Chapter.objects.filter(volume__isnull=True)
        for chapter in invalid_chapters:
            self.stdout.write(f'Removing invalid chapter: {chapter.id}')
            chapter.delete()
        
        # Fix chapters without slugs
        chapters_without_slugs = Chapter.objects.filter(slug__isnull=True) | Chapter.objects.filter(slug='')
        for chapter in chapters_without_slugs:
            chapter.save()  # This will trigger slug generation
            self.stdout.write(f'Fixed chapter slug: {chapter.title}')

    def create_admin_user(self):
        """Create admin user"""
        admin_email = 'admin@docwn.com'
        
        # Try to find existing admin user by email or username
        admin = User.objects.filter(email=admin_email).first()
        if not admin:
            admin = User.objects.filter(username='admin').first()
        
        if admin:
            return admin
            
        # Try different admin credentials if default ones exist
        try:
            admin = User.objects.create_user(
                email=admin_email,
                username='admin',
                password='admin123',
                role=UserRole.WEBSITE_ADMIN.value,
                is_staff=True,
                is_superuser=True,
                is_email_verified=True
            )
        except:
            # If admin username exists, try admin2
            try:
                admin = User.objects.create_user(
                    email='admin2@docwn.com',
                    username='admin2',
                    password='admin123',
                    role=UserRole.WEBSITE_ADMIN.value,
                    is_staff=True,
                    is_superuser=True,
                    is_email_verified=True
                )
            except:
                # Return any existing admin-like user
                admin = User.objects.filter(is_staff=True).first()
                if not admin:
                    admin = User.objects.first()
                if admin:
                    return admin
                raise Exception("Could not create or find admin user")
        
        if hasattr(admin, 'profile'):
            profile = admin.profile
            profile.display_name = 'Administrator'
            profile.description = 'Website Administrator'
            profile.save()
        
        return admin

    def create_sample_users(self):
        """Create sample users for testing"""
        users_data = [
            ('user1@test.com', 'testuser1', 'Nguyễn Văn A', 'Người dùng thích đọc light novel'),
            ('user2@test.com', 'testuser2', 'Trần Thị B', 'Fan của thể loại romance'),
            ('author1@test.com', 'testauthor1', 'Lê Văn C', 'Tác giả trẻ tài năng'),
            ('reader1@test.com', 'testreader1', 'Phạm Thị D', 'Độc giả nhiệt tình'),
            ('reviewer1@test.com', 'testreviewer1', 'Hoàng Văn E', 'Chuyên gia đánh giá'),
        ]
        
        users = []
        for email, username, display_name, description in users_data:
            # Check if user already exists by email or username
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.filter(username=username).first()
            
            if not user:
                try:
                    user = User.objects.create_user(
                        email=email,
                        username=username,
                        password='password123',
                        role=UserRole.USER.value,
                        is_email_verified=True
                    )
                    
                    if hasattr(user, 'profile'):
                        profile = user.profile
                        profile.display_name = display_name
                        profile.description = description
                        profile.gender = random.choice([g.value for g in Gender])
                        profile.birthday = fake.date_of_birth(minimum_age=16, maximum_age=50)
                        profile.save()
                except Exception as e:
                    self.stdout.write(f'Could not create user {username}: {e}')
                    continue
                    
            users.append(user)
                
        return users

    def create_sample_authors(self):
        """Create sample authors"""
        authors_data = [
            ('Nguyễn Nhật Ánh', 'Tác giả nổi tiếng Việt Nam với nhiều tác phẩm về tuổi thơ'),
            ('Haruki Murakami', 'Nhà văn Nhật Bản được yêu thích trên toàn thế giới'),
            ('J.K. Rowling', 'Tác giả series Harry Potter nổi tiếng'),
            ('Tô Hoài', 'Tác giả "Dế Mèn phiêu lưu ký"'),
            ('Stephen King', 'Vua của thể loại kinh dị'),
        ]
        
        authors = []
        for name, description in authors_data:
            if not Author.objects.filter(name=name).exists():
                author = Author.objects.create(
                    name=name,
                    description=description,
                    birthday=fake.date_of_birth(minimum_age=30, maximum_age=80),
                    gender=random.choice([g.value for g in Gender]),
                    country=fake.country(),
                    image_url=f'https://picsum.photos/300/400?random={len(authors)+100}'
                )
                authors.append(author)
                
        return authors

    def create_sample_artists(self):
        """Create sample artists"""
        artists_data = [
            ('Takeshi Obata', 'Nghệ sĩ vẽ manga nổi tiếng'),
            ('Akira Toriyama', 'Tác giả Dragon Ball'),
            ('Eiichiro Oda', 'Tác giả One Piece'),
        ]
        
        artists = []
        for name, description in artists_data:
            if not Artist.objects.filter(name=name).exists():
                artist = Artist.objects.create(
                    name=name,
                    description=description,
                    birthday=fake.date_of_birth(minimum_age=25, maximum_age=70),
                    gender=random.choice([g.value for g in Gender]),
                    country=fake.country(),
                    image_url=f'https://picsum.photos/300/400?random={len(artists)+200}'
                )
                artists.append(artist)
                
        return artists

    def create_sample_tags(self):
        """Create sample tags"""
        tags_data = [
            ('Lãng mạn', 'Thể loại tình cảm, lãng mạn'),
            ('Hành động', 'Thể loại hành động, phiêu lưu'),
            ('Kinh dị', 'Thể loại kinh dị, ma quái'),
            ('Fantasy', 'Thể loại giả tưởng, phép thuật'),
            ('Học đường', 'Bối cảnh học đường, thanh xuân'),
            ('Isekai', 'Thể loại chuyển sinh, thế giới khác'),
            ('Slice of Life', 'Cuộc sống thường ngày'),
            ('Trinh thám', 'Thể loại bí ẩn, trinh thám'),
            ('Sci-Fi', 'Khoa học viễn tưởng'),
            ('Hài hước', 'Thể loại hài hước, comedy'),
        ]
        
        tags = []
        for name, description in tags_data:
            slug = name.lower().replace(' ', '-').replace(',', '')
            if not Tag.objects.filter(slug=slug).exists():
                tag = Tag.objects.create(
                    name=name,
                    slug=slug,
                    description=description
                )
                tags.append(tag)
                
        return tags

    def create_sample_novels(self, users, authors, artists, tags):
        """Create sample novels"""
        novels_data = [
            {
                'name': 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh',
                'summary': 'Câu chuyện về tuổi thơ gắn liền với những kỷ niệm đẹp ở quê nhà. Một tác phẩm kinh điển của văn học Việt Nam.',
                'progress_status': ProgressStatus.COMPLETED.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Slice of Life', 'Lãng mạn']
            },
            {
                'name': 'Chuyển Sinh Thành Ma Vương Tối Thượng',
                'summary': 'Sau khi chết trong một tai nạn, nhân vật chính được chuyển sinh thành ma vương trong thế giới fantasy. Liệu anh ta có thể thích nghi với cuộc sống mới?',
                'progress_status': ProgressStatus.ONGOING.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Isekai', 'Fantasy', 'Hành động']
            },
            {
                'name': 'Học Viện Anh Hùng: Câu Chuyện Thanh Xuân',
                'summary': 'Trong một thế giới nơi siêu năng lực là điều bình thường, một cậu bé không có năng lực vẫn theo đuổi ước mơ trở thành anh hùng.',
                'progress_status': ProgressStatus.ONGOING.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Học đường', 'Hành động', 'Fantasy']
            },
            {
                'name': 'Bí Ẩn Thành Phố Đêm',
                'summary': 'Một thám tử tài ba phải giải quyết những vụ án bí ẩn trong thành phố. Mỗi vụ án đều ẩn chứa những bí mật đen tối.',
                'progress_status': ProgressStatus.COMPLETED.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Trinh thám', 'Kinh dị']
            },
            {
                'name': 'Tình Yêu Tuổi 17',
                'summary': 'Câu chuyện tình yêu ngọt ngào giữa hai học sinh trung học. Họ cùng nhau trải qua những khoảnh khắc đẹp nhất của tuổi thanh xuân.',
                'progress_status': ProgressStatus.ONGOING.value,
                'approval_status': ApprovalStatus.PENDING.value,
                'tags': ['Lãng mạn', 'Học đường', 'Slice of Life']
            },
            {
                'name': 'Chiến Tranh Giữa Các Vì Sao',
                'summary': 'Trong tương lai xa, nhân loại đã du hành vũ trụ. Một cuộc chiến khốc liệt nổ ra giữa các hành tinh vì quyền kiểm soát thiên hà.',
                'progress_status': ProgressStatus.SUSPEND.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Sci-Fi', 'Hành động']
            },
            {
                'name': 'Nhật Ký Của Một Otaku',
                'summary': 'Cuộc sống hài hước của một otaku và những tình huống dở khóc dở cười anh ta gặp phải hàng ngày.',
                'progress_status': ProgressStatus.ONGOING.value,
                'approval_status': ApprovalStatus.APPROVED.value,
                'tags': ['Hài hước', 'Slice of Life']
            },
            {
                'name': 'Ma Pháp Sư Tân Binh',
                'summary': 'Trong một thế giới đầy phép thuật, một pháp sư trẻ tuổi bắt đầu cuộc hành trình khám phá sức mạnh của mình.',
                'progress_status': ProgressStatus.ONGOING.value,
                'approval_status': ApprovalStatus.DRAFT.value,
                'tags': ['Fantasy', 'Hành động']
            },
        ]
        
        novels = []
        for i, novel_data in enumerate(novels_data):
            if not Novel.objects.filter(name=novel_data['name']).exists():
                # Ensure we have a valid slug
                name = novel_data['name']
                summary = novel_data['summary']
                
                novel = Novel.objects.create(
                    name=name,
                    summary=summary,
                    author=random.choice(authors) if authors else None,
                    artist=random.choice(artists) if artists and random.random() < 0.7 else None,
                    image_url=f'https://picsum.photos/300/400?random={i+500}',
                    progress_status=novel_data['progress_status'],
                    approval_status=novel_data['approval_status'],
                    word_count=random.randint(10000, 200000),
                    view_count=random.randint(100, 10000),
                    favorite_count=random.randint(10, 1000),
                    rating_avg=round(random.uniform(3.0, 5.0), 1),
                    created_by=random.choice(users),
                    created_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
                )
                
                # Verify slug was created properly
                if not novel.slug:
                    novel.slug = f'novel-{i+1}'
                    novel.save(update_fields=['slug'])
                
                # Assign tags
                for tag_name in novel_data['tags']:
                    tag = Tag.objects.filter(name=tag_name).first()
                    if tag:
                        try:
                            NovelTag.objects.create(novel=novel, tag=tag)
                        except:
                            pass
                
                novels.append(novel)
                
        return novels

    def create_sample_volumes(self, novels):
        """Create sample volumes"""
        volumes = []
        for novel in novels:
            # Ensure novel has a valid slug
            if not novel.slug:
                novel.slug = f'novel-{novel.id}'
                novel.save(update_fields=['slug'])
                
            volume_count = random.randint(1, 3)
            for i in range(volume_count):
                volume = Volume.objects.create(
                    novel=novel,
                    name=f'Tập {i+1}',
                    position=i+1
                )
                volumes.append(volume)
        return volumes

    def create_sample_chapters(self, volumes):
        """Create sample chapters"""
        chapters = []
        chapter_titles = [
            'Khởi đầu', 'Cuộc gặp gỡ định mệnh', 'Bí mật được hé lộ',
            'Thử thách đầu tiên', 'Tình bạn và phản bội', 'Cuộc chiến quyết định',
            'Sự thật đau lòng', 'Hy sinh cao cả', 'Chiến thắng và mất mát',
            'Khởi đầu mới'
        ]
        
        for volume in volumes:
            # Ensure volume has a proper novel relationship
            if not volume.novel or not volume.novel.slug:
                self.stdout.write(f'Warning: Volume {volume.id} has invalid novel relationship')
                continue
                
            chapter_count = random.randint(5, 10)
            for i in range(chapter_count):
                title = f"Chương {i+1}: {random.choice(chapter_titles)}"
                chapter = Chapter.objects.create(
                    volume=volume,
                    title=title,
                    position=i+1,
                    word_count=random.randint(1000, 5000),
                    view_count=random.randint(50, 2000),
                    approved=True
                )
                
                # Verify chapter has proper slug
                if not chapter.slug:
                    chapter.slug = f'chuong-{i+1}-{chapter.id}'
                    chapter.save(update_fields=['slug'])
                    
                chapters.append(chapter)
        return chapters

    def create_sample_chunks(self, chapters):
        """Create sample chunks with realistic content"""
        chunks = []
        sample_contents = [
            "Ngày hôm đó, trời rất đẹp. Những tia nắng vàng len lỏi qua kẽ lá, tạo nên những vệt sáng lung linh trên mặt đất. Tôi bước đi trên con đường quen thuộc về nhà, tâm trí đầy những suy nghĩ về những gì vừa xảy ra.",
            
            "Cô ấy nhìn tôi từ xa, đôi mắt long lanh như có chứa đựng cả một vũ trụ. Lần đầu tiên trong đời, tôi cảm thấy tim mình đập thình thịch như vậy. Có phải đây chính là tình yêu đột ngột mà mọi người thường nói đến?",
            
            "Âm thanh của những thanh kiếm va chạm vang vọng khắp chiến trường. Máu và mồ hôi đã thấm ướt mặt đất, nhưng không ai dám lùi bước. Đây là cuộc chiến để bảo vệ những gì chúng tôi yêu thương nhất.",
            
            "Trong căn phòng tối tăm ấy, tôi cảm thấy có thứ gì đó đang quan sát mình. Lạnh gáy chạy dọc theo sống lưng, tôi cố gắng bình tĩnh nhưng không thể kiểm soát được nỗi sợ hãi đang dâng lên.",
            
            "Công nghệ đã phát triển đến mức con người và robot có thể sống chung hòa bình. Nhưng liệu điều này có thực sự tốt? Hay chúng ta đang đánh mất thứ gì đó quan trọng của bản chất con người?",
        ]
        
        for chapter in chapters:
            # Ensure chapter has valid relationships
            if not chapter.volume or not chapter.volume.novel:
                self.stdout.write(f'Warning: Chapter {chapter.id} has invalid relationships')
                continue
                
            chunk_count = random.randint(3, 8)
            for i in range(chunk_count):
                content = random.choice(sample_contents)
                if random.random() < 0.5:
                    content += f"\n\n{fake.text(max_nb_chars=200)}"
                
                chunk = Chunk.objects.create(
                    chapter=chapter,
                    position=i+1,
                    content=content,
                    word_count=len(content.split())
                )
                chunks.append(chunk)
        return chunks

    def create_sample_interactions(self, users, novels, chapters):
        """Create sample interactions"""
        # Favorites
        for user in users:
            favorite_novels = random.sample(novels, min(random.randint(1, 5), len(novels)))
            for novel in favorite_novels:
                try:
                    Favorite.objects.create(user=user, novel=novel)
                except:
                    pass
        
        # Reading History
        for user in users:
            read_chapters = random.sample(chapters, min(random.randint(5, 20), len(chapters)))
            for chapter in read_chapters:
                try:
                    ReadingHistory.objects.create(
                        user=user,
                        chapter=chapter,
                        novel=chapter.volume.novel,
                        reading_progress=round(random.uniform(0.1, 1.0), 2)
                    )
                except:
                    pass
        
        # Comments
        comment_templates = [
            "Truyện hay quá! Tôi rất thích cách tác giả xây dựng cốt truyện.",
            "Chapter này cảm động quá, tôi đọc mà muốn khóc.",
            "Nhân vật chính rất thú vị, mong chờ sự phát triển tiếp theo.",
            "Plot twist bất ngờ quá! Không ngờ được.",
            "Tác giả viết rất hay, recommend cho mọi người.",
        ]
        
        for novel in novels:
            comment_count = random.randint(2, 8)
            for _ in range(comment_count):
                user = random.choice(users)
                content = random.choice(comment_templates)
                Comment.objects.create(
                    user=user,
                    novel=novel,
                    content=content,
                    like_count=random.randint(0, 20)
                )
        
        # Reviews
        review_templates = {
            5: "Xuất sắc! Một tác phẩm tuyệt vời mà ai cũng nên đọc.",
            4: "Rất hay! Cốt truyện hấp dẫn và nhân vật được xây dựng tốt.",
            3: "Ổn, đọc được. Có những phần hay nhưng cũng có phần chậm.",
            2: "Hơi thất vọng. Cốt truyện không được logic lắm.",
            1: "Thất vọng hoàn toàn. Không thể theo dõi được cốt truyện.",
        }
        
        for novel in novels:
            review_count = random.randint(1, 5)
            review_users = random.sample(users, min(review_count, len(users)))
            for user in review_users:
                try:
                    rating = random.randint(3, 5)  # Mostly positive reviews
                    content = review_templates[rating]
                    Review.objects.create(
                        user=user,
                        novel=novel,
                        rating=rating,
                        content=content
                    )
                except:
                    pass
        
        # Notifications
        for user in users:
            notification_count = random.randint(1, 5)
            for _ in range(notification_count):
                Notification.objects.create(
                    user=user,
                    type=random.choice(['new_chapter', 'new_comment', 'system_announcement']),
                    content=f"Thông báo test cho {user.username}",
                    is_read=random.choice([True, False])
                )
