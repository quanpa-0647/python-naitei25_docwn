import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
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

fake = Faker(['vi_VN', 'en_US', 'ja_JP'])


class Command(BaseCommand):
    help = 'Generate comprehensive test data for the entire web application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--authors',
            type=int,
            default=25,
            help='Number of authors to create'
        )
        parser.add_argument(
            '--artists',
            type=int,
            default=20,
            help='Number of artists to create'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=30,
            help='Number of tags to create'
        )
        parser.add_argument(
            '--novels',
            type=int,
            default=100,
            help='Number of novels to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before generating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
            
        self.stdout.write('Starting data generation...')
        
        # First, clean up any bad data
        self.cleanup_bad_data()
        
        try:
            # Core data
            users = self.create_users(options['users'])
            authors = self.create_authors(options['authors'])
            artists = self.create_artists(options['artists'])
            tags = self.create_tags(options['tags'])
            
            # Content data
            novels = self.create_novels(options['novels'], users, authors, artists, tags)
            volumes = self.create_volumes(novels)
            chapters = self.create_chapters(volumes)
            chunks = self.create_chunks(chapters)
            
            # Interaction data
            self.create_favorites(users, novels)
            self.create_reading_history(users, chapters, novels)
            comments = self.create_comments(users, novels)
            reviews = self.create_reviews(users, novels)
            self.create_notifications(users)
            self.create_reports(users, comments, reviews)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated comprehensive test data:\\n'
                    f'- {len(users)} users\\n'
                    f'- {len(authors)} authors\\n'
                    f'- {len(artists)} artists\\n'
                    f'- {len(tags)} tags\\n'
                    f'- {len(novels)} novels\\n'
                    f'- {len(volumes)} volumes\\n'
                    f'- {len(chapters)} chapters\\n'
                    f'- {len(chunks)} chunks\\n'
                    f'- Favorites, reading history, comments, reviews, notifications, and reports created'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during data generation: {e}')
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

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            Report, Notification, Comment, Review, ReadingHistory, Favorite,
            Chunk, Chapter, Volume, NovelTag, Novel, Tag, Artist, Author,
            UserProfile, User
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Cleared {count} {model.__name__} records')

    def create_users(self, count):
        """Create diverse users with different roles and profiles"""
        self.stdout.write(f'Creating {count} users...')
        users = []
        
        # Check for existing admin users first (outside transaction to avoid conflicts)
        existing_admins = list(User.objects.filter(role=UserRole.WEBSITE_ADMIN.value))
        if existing_admins:
            users.extend(existing_admins[:1])  # Add one existing admin
            self.stdout.write(f'Found existing admin user: {existing_admins[0].username}')
        else:
            # Try to create admin user
            admin_email = 'testadmin@docwn.com'
            admin_username = 'testadmin'
            
            if not User.objects.filter(email=admin_email).exists() and not User.objects.filter(username=admin_username).exists():
                try:
                    admin = User.objects.create_user(
                        email=admin_email,
                        username=admin_username,
                        password='admin123',
                        role=UserRole.WEBSITE_ADMIN.value,
                        is_staff=True,
                        is_superuser=True,
                        is_email_verified=True
                    )
                    users.append(admin)
                    self.stdout.write(f'Created admin user: {admin_username}')
                except Exception as e:
                    self.stdout.write(f'Could not create admin user: {e}')
                    # Try to find any existing staff user
                    staff_user = User.objects.filter(is_staff=True).first()
                    if staff_user:
                        users.append(staff_user)
            
        # Create regular users
        for i in range(max(0, count - len(users))):
            try:
                email = f'testuser{i+1000}@example.com'
                username = f'testuser{i+1000}'
                
                # Skip if already exists
                if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
                    continue
                
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='password123',
                    role=random.choice([UserRole.USER.value, UserRole.WEBSITE_ADMIN.value]),
                    is_email_verified=random.choice([True, False]),
                    is_blocked=random.choice([True, False]) if random.random() < 0.1 else False
                )
                
                # Create profile
                if hasattr(user, 'profile'):
                    profile = user.profile
                    profile.display_name = fake.name()
                    profile.gender = random.choice([g.value for g in Gender])
                    profile.birthday = fake.date_of_birth(minimum_age=13, maximum_age=80)
                    profile.description = fake.text(max_nb_chars=200) if random.random() < 0.7 else None
                    profile.interest = fake.text(max_nb_chars=150) if random.random() < 0.6 else None
                    profile.save()
                
                users.append(user)
                
            except Exception as e:
                self.stdout.write(f'Error creating user {i}: {e}')
                continue
                
        return users

    def create_authors(self, count):
        """Create diverse authors"""
        self.stdout.write(f'Creating {count} authors...')
        authors = []
        
        # Famous Vietnamese authors
        vietnamese_authors = [
            ('Nguyễn Nhật Ánh', 'Một trong những tác giả được yêu thích nhất Việt Nam'),
            ('Tô Hoài', 'Tác giả nổi tiếng với "Dế Mèn phiêu lưu ký"'),
            ('Vũ Trọng Phụng', 'Nhà văn hiện thực phê phán'),
            ('Nam Cao', 'Tác giả của "Chí Phèo", "Lão Hạc"'),
            ('Ngô Tất Tố', 'Tác giả "Tắt đèn"'),
        ]
        
        # International authors  
        international_authors = [
            ('Haruki Murakami', 'Nhà văn Nhật Bản nổi tiếng thế giới'),
            ('J.K. Rowling', 'Tác giả series Harry Potter'),
            ('Stephen King', 'Vua của thể loại kinh dị'),
            ('Agatha Christie', 'Nữ hoàng truyện trinh thám'),
            ('George Orwell', 'Tác giả "1984" và "Animal Farm"'),
        ]
        
        famous_authors = vietnamese_authors + international_authors
        
        for i, (name, desc) in enumerate(famous_authors[:min(count, len(famous_authors))]):
            try:
                # Check if author already exists
                if Author.objects.filter(name=name).exists():
                    authors.append(Author.objects.get(name=name))
                    continue
                    
                author = Author.objects.create(
                    name=name,
                    pen_name=fake.name() if random.random() < 0.3 else None,
                    description=desc,
                    birthday=fake.date_of_birth(minimum_age=30, maximum_age=90),
                    deathday=fake.date_between(start_date='-20y', end_date='today') if random.random() < 0.2 else None,
                    gender=random.choice([g.value for g in Gender]),
                    country=fake.country(),
                    image_url=f'https://picsum.photos/300/400?random={i}'
                )
                authors.append(author)
            except Exception as e:
                self.stdout.write(f'Error creating famous author {name}: {e}')
                continue
            
        # Create remaining random authors
        for i in range(len(famous_authors), count):
            try:
                name = fake.unique.name()
                attempts = 0
                while Author.objects.filter(name=name).exists() and attempts < 10:
                    fake.unique.clear()  # Clear the unique cache
                    name = fake.unique.name()
                    attempts += 1
                
                if attempts >= 10:
                    name = f"Author {i}_{random.randint(1000, 9999)}"
                    
                author = Author.objects.create(
                    name=name,
                    pen_name=fake.name() if random.random() < 0.3 else None,
                    description=fake.text(max_nb_chars=300),
                    birthday=fake.date_of_birth(minimum_age=20, maximum_age=80),
                    deathday=fake.date_between(start_date='-10y', end_date='today') if random.random() < 0.1 else None,
                    gender=random.choice([g.value for g in Gender]),
                    country=fake.country(),
                    image_url=f'https://picsum.photos/300/400?random={i+100}'
                )
                authors.append(author)
            except Exception as e:
                self.stdout.write(f'Error creating author {i}: {e}')
                continue
                
        return authors

    def create_artists(self, count):
        """Create diverse artists"""
        self.stdout.write(f'Creating {count} artists...')
        artists = []
        
        for i in range(count):
            try:
                name = fake.unique.name()
                attempts = 0
                while Artist.objects.filter(name=name).exists() and attempts < 10:
                    fake.unique.clear()  # Clear the unique cache
                    name = fake.unique.name()
                    attempts += 1
                
                if attempts >= 10:
                    name = f"Artist {i}_{random.randint(1000, 9999)}"
                    
                artist = Artist.objects.create(
                    name=name,
                    pen_name=fake.name() if random.random() < 0.4 else None,
                    description=fake.text(max_nb_chars=250),
                    birthday=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    deathday=fake.date_between(start_date='-5y', end_date='today') if random.random() < 0.05 else None,
                    gender=random.choice([g.value for g in Gender]),
                    country=fake.country(),
                    image_url=f'https://picsum.photos/300/400?random={i+200}'
                )
                artists.append(artist)
            except Exception as e:
                self.stdout.write(f'Error creating artist {i}: {e}')
                continue
                
        return artists

    def create_tags(self, count):
        """Create diverse tags for categorizing novels"""
        self.stdout.write(f'Creating {count} tags...')
        
        # Predefined popular tags
        popular_tags = [
            ('Lãng mạn', 'Thể loại tình cảm, lãng mạn'),
            ('Hành động', 'Thể loại hành động, phiêu lưu'),
            ('Kinh dị', 'Thể loại kinh dị, ma quái'),
            ('Trinh thám', 'Thể loại trinh thám, bí ẩn'),
            ('Khoa học viễn tưởng', 'Thể loại khoa học viễn tưởng'),
            ('Fantasy', 'Thể loại giả tưởng, phép thuật'),
            ('Học đường', 'Bối cảnh học đường, thanh xuân'),
            ('Isekai', 'Thể loại chuyển sinh, du hành thế giới khác'),
            ('Harem', 'Thể loại harem, đa tình'),
            ('Slice of Life', 'Thể loại cuộc sống thường ngày'),
            ('Mecha', 'Thể loại robot, máy móc'),
            ('Siêu nhiên', 'Thể loại siêu nhiên, phép thuật'),
            ('Lịch sử', 'Bối cảnh lịch sử'),
            ('Quân sự', 'Thể loại quân sự, chiến tranh'),
            ('Thể thao', 'Thể loại thể thao'),
            ('Ẩm thực', 'Thể loại ẩm thực, nấu ăn'),
            ('Âm nhạc', 'Thể loại âm nhạc'),
            ('Game', 'Thể loại game, thế giới ảo'),
            ('Tâm lý', 'Thể loại tâm lý, drama'),
            ('Hài hước', 'Thể loại hài hước, comedy'),
            ('Tragedy', 'Thể loại bi kịch'),
            ('Shounen', 'Dành cho nam thiếu niên'),
            ('Shoujo', 'Dành cho nữ thiếu niên'),
            ('Seinen', 'Dành cho nam thanh niên'),
            ('Josei', 'Dành cho nữ thanh niên'),
            ('Ecchi', 'Thể loại ecchi'),
            ('Yuri', 'Thể loại yuri'),
            ('Yaoi', 'Thể loại yaoi'),
            ('Vampire', 'Ma cà rồng'),
            ('Zombie', 'Xác sống'),
        ]
        
        tags = []
        for i, (name, desc) in enumerate(popular_tags[:count]):
            try:
                slug = name.lower().replace(' ', '-').replace(',', '')
                
                # Check if tag already exists
                if Tag.objects.filter(name=name).exists() or Tag.objects.filter(slug=slug).exists():
                    existing_tag = Tag.objects.filter(name=name).first() or Tag.objects.filter(slug=slug).first()
                    tags.append(existing_tag)
                    continue
                    
                tag = Tag.objects.create(
                    name=name,
                    slug=slug,
                    description=desc
                )
                tags.append(tag)
            except Exception as e:
                self.stdout.write(f'Error creating tag {name}: {e}')
                continue
                
        return tags

    def create_novels(self, count, users, authors, artists, tags):
        """Create diverse novels with rich metadata"""
        self.stdout.write(f'Creating {count} novels...')
        novels = []
        
        # Novel title templates for different genres
        novel_titles = [
            # Romance
            'Tình Yêu Đầu Tiên', 'Anh Và Em', 'Trái Tim Tan Vỡ', 'Mối Tình Đầu',
            'Yêu Em Từ Cái Nhìn Đầu Tiên', 'Hạnh Phúc Bên Anh',
            
            # Fantasy/Isekai
            'Chuyển Sinh Thành Ma Vương', 'Tôi Là Anh Hùng Của Thế Giới Khác',
            'Phép Thuật Trong Học Viện', 'Hiệp Sĩ Rồng Thiêng',
            'Thế Giới Phép Thuật', 'Vương Quốc Elf',
            
            # Action/Adventure
            'Chiến Binh Vô Địch', 'Ninja Huyền Thoại', 'Kiếm Sĩ Bất Bại',
            'Cuộc Chiến Cuối Cùng', 'Anh Hùng Vô Danh', 'Sát Thủ Bóng Đêm',
            
            # Horror/Mystery
            'Bí Ẩn Ngôi Nhà Cũ', 'Ma Lai Đêm Khuya', 'Án Mạng Kinh Hoàng',
            'Kẻ Săn Đầu Người', 'Linh Hồn Báo Thù', 'Bóng Ma Trong Gương',
            
            # Sci-Fi
            'Du Hành Thời Gian', 'Robot Biết Yêu', 'Chinh Phục Sao Hỏa',
            'Thế Giới Ảo', 'AI Nổi Loạn', 'Tương Lai Đen Tối',
            
            # School/Youth
            'Thanh Xuân Của Chúng Ta', 'Tuổi 17', 'Kỷ Niệm Học Trò',
            'Mối Tình Học Trò', 'Lớp Học Đặc Biệt', 'Câu Lạc Bộ Văn Học',
        ]
        
        # Sample summaries by genre
        romance_summaries = [
            'Một câu chuyện tình yêu ngọt ngào giữa hai người trẻ. Họ gặp nhau trong hoàn cảnh đặc biệt và dần phát triển tình cảm.',
            'Mối tình đầu đẹp như mơ của cô gái 17 tuổi với chàng trai cùng trường.',
            'Câu chuyện về tình yêu vượt qua mọi khó khăn, thử thách của cuộc sống.',
        ]
        
        fantasy_summaries = [
            'Một thế giới đầy phép thuật nơi anh hùng trẻ tuổi bắt đầu cuộc hành trình tìm kiếm sức mạnh.',
            'Sau khi chuyển sinh sang thế giới khác, nhân vật chính phải học cách sinh tồn với sức mạnh mới.',
            'Câu chuyện về cuộc chiến giữa ánh sáng và bóng tối trong thế giới fantasy.',
        ]
        
        action_summaries = [
            'Một chiến binh trẻ tuổi phải đối mặt với những thử thách khắc nghiệt để trở thành mạnh nhất.',
            'Cuộc phiêu lưu đầy nguy hiểm của nhóm anh hùng trong thế giới hậu tận thế.',
            'Câu chuyện về sự trả thù và công lý trong thế giới tội phạm.',
        ]
        
        for i in range(count):
            try:
                # Random title (either from templates or generated)
                if random.random() < 0.7 and novel_titles:
                    base_title = random.choice(novel_titles)
                    title = f"{base_title} {random.choice(['', 'II', 'III', '- Phần 2', '- Tập Cuối', '- Truyền Thuyết'])}"
                else:
                    title = fake.sentence(nb_words=random.randint(3, 8)).replace('.', '')
                
                # Ensure uniqueness
                while Novel.objects.filter(name=title).exists():
                    title = f"{title} {random.randint(1, 999)}"
                
                # Random summary based on genre
                genre_type = random.choice(['romance', 'fantasy', 'action', 'general'])
                if genre_type == 'romance':
                    summary = random.choice(romance_summaries)
                elif genre_type == 'fantasy':
                    summary = random.choice(fantasy_summaries)
                elif genre_type == 'action':
                    summary = random.choice(action_summaries)
                else:
                    summary = fake.text(max_nb_chars=500)
                
                # Random creation date (last 2 years)
                created_at = fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
                
                novel = Novel.objects.create(
                    name=title,
                    summary=summary,
                    author=random.choice(authors) if random.random() < 0.9 else None,
                    artist=random.choice(artists) if random.random() < 0.7 else None,
                    image_url=f'https://picsum.photos/300/400?random={i+500}',
                    progress_status=random.choice([s.value for s in ProgressStatus]),
                    approval_status=random.choice([s.value for s in ApprovalStatus]),
                    other_names=fake.sentence() if random.random() < 0.3 else None,
                    word_count=random.randint(5000, 500000),
                    view_count=random.randint(0, 50000),
                    favorite_count=random.randint(0, 5000),
                    rating_avg=round(random.uniform(1.0, 5.0), 1),
                    created_by=random.choice(users),
                    is_anonymous=random.choice([True, False]) if random.random() < 0.1 else False,
                    created_at=created_at,
                    updated_at=fake.date_time_between(start_date=created_at, end_date='now', tzinfo=timezone.get_current_timezone()),
                    rejected_reason=fake.text(max_nb_chars=200) if random.random() < 0.1 else None
                )
                
                # Verify slug was created properly
                if not novel.slug:
                    novel.slug = f'novel-{i+1}'
                    novel.save(update_fields=['slug'])
                
                # Assign random tags (2-5 tags per novel)
                novel_tags = random.sample(tags, min(random.randint(2, 5), len(tags)))
                for tag in novel_tags:
                    try:
                        NovelTag.objects.create(novel=novel, tag=tag)
                    except:
                        pass  # Skip if already exists
                
                novels.append(novel)
                
            except Exception as e:
                self.stdout.write(f'Error creating novel {i}: {e}')
                continue
                
        return novels

    def create_volumes(self, novels):
        """Create volumes for novels"""
        self.stdout.write(f'Creating volumes for {len(novels)} novels...')
        volumes = []
        
        for novel in novels:
            # Ensure novel has a valid slug
            if not novel.slug:
                novel.slug = f'novel-{novel.id}'
                novel.save(update_fields=['slug'])
                
            # Each novel has 1-5 volumes
            volume_count = random.randint(1, 5)
            
            for i in range(volume_count):
                try:
                    volume_names = [
                        f'Tập {i+1}', f'Volume {i+1}', f'Phần {i+1}',
                        f'Chương {i+1}', f'Quyển {i+1}'
                    ]
                    
                    volume = Volume.objects.create(
                        novel=novel,
                        name=random.choice(volume_names),
                        position=i + 1
                    )
                    volumes.append(volume)
                except Exception as e:
                    self.stdout.write(f'Error creating volume for novel {novel.name}: {e}')
                    continue
                    
        return volumes

    def create_chapters(self, volumes):
        """Create chapters for volumes"""
        self.stdout.write(f'Creating chapters for {len(volumes)} volumes...')
        chapters = []
        
        chapter_title_templates = [
            'Khởi đầu', 'Cuộc gặp gỡ', 'Bí mật', 'Thử thách', 'Khám phá',
            'Nguy hiểm', 'Quyết đấu', 'Tình bạn', 'Hy sinh', 'Chiến thắng',
            'Tình yêu', 'Chia ly', 'Trở về', 'Kết thúc', 'Bắt đầu mới',
            'Bóng tối', 'Ánh sáng', 'Hy vọng', 'Tuyệt vọng', 'Sự thật'
        ]
        
        for volume in volumes:
            # Ensure volume has a proper novel relationship
            if not volume.novel or not volume.novel.slug:
                self.stdout.write(f'Warning: Volume {volume.id} has invalid novel relationship')
                continue
                
            # Each volume has 5-20 chapters
            chapter_count = random.randint(5, 20)
            
            for i in range(chapter_count):
                try:
                    title = f"Chương {i+1}: {random.choice(chapter_title_templates)}"
                    if random.random() < 0.3:
                        title += f" - {fake.sentence(nb_words=3).replace('.', '')}"
                    
                    chapter = Chapter.objects.create(
                        volume=volume,
                        title=title,
                        position=i + 1,
                        word_count=random.randint(500, 5000),
                        view_count=random.randint(0, 10000),
                        approved=random.choice([True, False]) if random.random() < 0.9 else True,
                        rejected_reason=fake.text(max_nb_chars=100) if random.random() < 0.05 else None,
                        is_hidden=random.choice([True, False]) if random.random() < 0.1 else False
                    )
                    
                    # Verify chapter has proper slug
                    if not chapter.slug:
                        chapter.slug = f'chuong-{i+1}-{chapter.id}'
                        chapter.save(update_fields=['slug'])
                        
                    chapters.append(chapter)
                except Exception as e:
                    self.stdout.write(f'Error creating chapter for volume {volume.name}: {e}')
                    continue
                    
        return chapters

    def create_chunks(self, chapters):
        """Create content chunks for chapters"""
        self.stdout.write(f'Creating chunks for {len(chapters)} chapters...')
        chunks = []
        
        sample_content = [
            "Ngày hôm đó, trời rất đẹp. Những tia nắng vàng len lỏi qua kẽ lá, tạo nên những vệt sáng lung linh trên mặt đất. Cô gái trẻ bước đi trên con đường quen thuộc, tâm trí đầy những suy nghĩ.",
            
            "Anh nhìn cô từ xa, tim đập thình thịch. Đây là lần đầu tiên anh cảm thấy như vậy. Tình yêu đột ngột ập đến, khiến anh bối rối không biết phải làm gì.",
            
            "Cuộc chiến đã bắt đầu. Tiếng kiếm va chạm vang lên khắp chiến trường. Những chiến binh dũng cảm không ngại hy sinh vì tự do và công lý.",
            
            "Trong căn phòng tối tăm, bóng ma xuất hiện. Ánh mắt đỏ rực nhìn thẳng vào linh hồn của nạn nhân. Tiếng kêu thảm thiết vang lên trong đêm khuya.",
            
            "Thế giới tương lai đầy những công nghệ hiện đại. Robot và con người sống chung, tạo nên một xã hội hoàn toàn mới. Nhưng liệu điều này có tốt không?",
            
            "Trường học là nơi những kỷ niệm đẹp nhất được tạo nên. Tiếng cười học trò vang vọng khắp hành lang, tạo nên bầu không khí tươi vui.",
            
            "Phép thuật tồn tại trong thế giới này. Những pháp sư mạnh mẽ có thể điều khiển nguyên tố, tạo nên những phép màu không tưởng.",
            
            "Cuộc hành trình tìm kiếm kho báu đã bắt đầu. Những hiểm nguy rình rập ở mọi nơi, nhưng phần thưởng cuối cùng xứng đáng với mọi nỗ lực.",
        ]
        
        for chapter in chapters:
            # Ensure chapter has valid relationships
            if not chapter.volume or not chapter.volume.novel:
                self.stdout.write(f'Warning: Chapter {chapter.id} has invalid relationships')
                continue
                
            # Each chapter has 3-10 chunks
            chunk_count = random.randint(3, 10)
            
            for i in range(chunk_count):
                try:
                    # Generate realistic content
                    content_pieces = random.sample(sample_content, min(random.randint(2, 4), len(sample_content)))
                    content = "\n\n".join(content_pieces)
                    
                    # Add some variation
                    if random.random() < 0.3:
                        content += f"\n\n{fake.text(max_nb_chars=300)}"
                    
                    chunk = Chunk.objects.create(
                        chapter=chapter,
                        position=i + 1,
                        content=content,
                        word_count=len(content.split())
                    )
                    chunks.append(chunk)
                except Exception as e:
                    self.stdout.write(f'Error creating chunk for chapter {chapter.title}: {e}')
                    continue
                    
        return chunks

    def create_favorites(self, users, novels):
        """Create favorite relationships"""
        self.stdout.write(f'Creating favorites...')
        
        for user in users:
            # Each user favorites 0-10 novels
            favorite_count = random.randint(0, 10)
            user_novels = random.sample(novels, min(favorite_count, len(novels)))
            
            for novel in user_novels:
                try:
                    Favorite.objects.create(
                        user=user,
                        novel=novel,
                        created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                    )
                except:
                    pass  # Skip if already exists

    def create_reading_history(self, users, chapters, novels):
        """Create reading history"""
        self.stdout.write(f'Creating reading history...')
        
        for user in users:
            # Each user has read 5-30 chapters
            read_count = random.randint(5, 30)
            user_chapters = random.sample(chapters, min(read_count, len(chapters)))
            
            for chapter in user_chapters:
                try:
                    ReadingHistory.objects.create(
                        user=user,
                        chapter=chapter,
                        novel=chapter.volume.novel,
                        read_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                        reading_progress=round(random.uniform(0.1, 1.0), 2)
                    )
                except:
                    pass  # Skip if already exists

    def create_comments(self, users, novels):
        """Create comments on novels"""
        self.stdout.write(f'Creating comments...')
        comments = []
        
        comment_templates = [
            "Truyện hay quá! Tôi rất thích.",
            "Cốt truyện hấp dẫn, character development tốt.",
            "Chờ đợi chapter tiếp theo!",
            "Tác giả viết rất hay, cảm ơn bạn.",
            "Phần này hơi buồn, nhưng rất cảm động.",
            "Nhân vật chính rất thú vị.",
            "Plot twist bất ngờ quá!",
            "Ending thật tuyệt vời.",
            "Mong tác giả ra thêm nhiều truyện hay.",
            "Đọc xong muốn đọc lại ngay.",
        ]
        
        for novel in novels:
            # Each novel has 0-20 comments
            comment_count = random.randint(0, 20)
            
            for _ in range(comment_count):
                try:
                    user = random.choice(users)
                    content = random.choice(comment_templates)
                    if random.random() < 0.3:
                        content += f" {fake.sentence()}"
                    
                    comment = Comment.objects.create(
                        user=user,
                        novel=novel,
                        content=content,
                        like_count=random.randint(0, 50),
                        is_reported=random.choice([True, False]) if random.random() < 0.05 else False,
                        created_at=fake.date_time_between(start_date='-3m', end_date='now', tzinfo=timezone.get_current_timezone())
                    )
                    comments.append(comment)
                    
                    # Some comments have replies
                    if random.random() < 0.2:
                        reply_count = random.randint(1, 3)
                        for _ in range(reply_count):
                            try:
                                reply_user = random.choice(users)
                                reply_content = f"@{user.username} {random.choice(comment_templates[:5])}"
                                
                                Comment.objects.create(
                                    user=reply_user,
                                    novel=novel,
                                    content=reply_content,
                                    parent_comment=comment,
                                    like_count=random.randint(0, 10),
                                    created_at=fake.date_time_between(start_date=comment.created_at, end_date='now', tzinfo=timezone.get_current_timezone())
                                )
                            except:
                                pass
                                
                except Exception as e:
                    self.stdout.write(f'Error creating comment: {e}')
                    continue
                    
        return comments

    def create_reviews(self, users, novels):
        """Create reviews for novels"""
        self.stdout.write(f'Creating reviews...')
        
        review_templates = {
            5: [
                "Xuất sắc! Một tác phẩm tuyệt vời mà ai cũng nên đọc.",
                "Hoàn hảo từ cốt truyện đến nhân vật. 5 sao xứng đáng!",
                "Đây là một trong những truyện hay nhất tôi từng đọc.",
            ],
            4: [
                "Rất hay! Có một vài điểm nhỏ cần cải thiện nhưng tổng thể rất tốt.",
                "Truyện hấp dẫn, giữ được độ tension từ đầu đến cuối.",
                "Tác giả viết rất hay, recommend cho mọi người.",
            ],
            3: [
                "Ổn, đọc được. Có những phần hay nhưng cũng có phần hơi chậm.",
                "Trung bình khá, phù hợp để giải trí.",
                "Không quá xuất sắc nhưng cũng không tệ.",
            ],
            2: [
                "Hơi thất vọng. Cốt truyện không được logic lắm.",
                "Có tiềm năng nhưng chưa được khai thác tốt.",
                "Một vài ý tưởng hay nhưng execution chưa tốt.",
            ],
            1: [
                "Thất vọng hoàn toàn. Không recommend.",
                "Cốt truyện rối và nhân vật không có chiều sâu.",
                "Rất khó đọc, không thể theo dõi được.",
            ]
        }
        
        for novel in novels:
            # Each novel has 0-15 reviews
            review_count = random.randint(0, 15)
            novel_users = random.sample(users, min(review_count, len(users)))
            
            for user in novel_users:
                try:
                    rating = random.randint(1, 5)
                    content = random.choice(review_templates[rating])
                    if random.random() < 0.5:
                        content += f" {fake.sentence()}"
                    
                    Review.objects.create(
                        user=user,
                        novel=novel,
                        rating=rating,
                        content=content,
                        created_at=fake.date_time_between(start_date='-2m', end_date='now', tzinfo=timezone.get_current_timezone())
                    )
                except:
                    pass  # Skip if already exists

    def create_notifications(self, users):
        """Create notifications for users"""
        self.stdout.write(f'Creating notifications...')
        
        notification_types = [
            'new_chapter', 'new_comment', 'new_review', 'new_favorite',
            'system_announcement', 'author_update', 'novel_approved',
            'novel_rejected', 'comment_reply', 'mention'
        ]
        
        notification_templates = {
            'new_chapter': "Chương mới đã được cập nhật cho truyện bạn theo dõi.",
            'new_comment': "Có bình luận mới trên truyện của bạn.",
            'new_review': "Có đánh giá mới cho truyện của bạn.",
            'new_favorite': "Có người đã thích truyện của bạn.",
            'system_announcement': "Thông báo hệ thống: Cập nhật tính năng mới.",
            'author_update': "Tác giả yêu thích của bạn có cập nhật mới.",
            'novel_approved': "Truyện của bạn đã được phê duyệt.",
            'novel_rejected': "Truyện của bạn cần chỉnh sửa.",
            'comment_reply': "Có người đã trả lời bình luận của bạn.",
            'mention': "Bạn được nhắc đến trong một bình luận.",
        }
        
        for user in users:
            # Each user has 0-10 notifications
            notification_count = random.randint(0, 10)
            
            for _ in range(notification_count):
                try:
                    notif_type = random.choice(notification_types)
                    content = notification_templates[notif_type]
                    
                    Notification.objects.create(
                        user=user,
                        type=notif_type,
                        content=content,
                        is_read=random.choice([True, False]),
                        created_at=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone())
                    )
                except Exception as e:
                    self.stdout.write(f'Error creating notification: {e}')
                    continue

    def create_reports(self, users, comments, reviews):
        """Create reports for inappropriate content"""
        self.stdout.write(f'Creating reports...')
        
        report_reasons = [
            "Nội dung không phù hợp",
            "Ngôn từ thô tục, xúc phạm",
            "Spam hoặc quảng cáo",
            "Vi phạm bản quyền",
            "Nội dung sai sự thật",
            "Phân biệt chủng tộc",
            "Bạo lực quá mức",
            "Nội dung 18+",
        ]
        
        # Report some comments
        reported_comments = random.sample(comments, min(len(comments)//10, 20))
        for comment in reported_comments:
            try:
                reporter = random.choice(users)
                if reporter != comment.user:  # Can't report own comment
                    Report.objects.create(
                        user=reporter,
                        comment=comment,
                        reason=random.choice(report_reasons),
                        created_at=fake.date_time_between(start_date=comment.created_at, end_date='now', tzinfo=timezone.get_current_timezone())
                    )
            except:
                pass
        
        # Report some reviews
        all_reviews = list(Review.objects.all())
        reported_reviews = random.sample(all_reviews, min(len(all_reviews)//15, 10))
        for review in reported_reviews:
            try:
                reporter = random.choice(users)
                if reporter != review.user:  # Can't report own review
                    Report.objects.create(
                        user=reporter,
                        review=review,
                        reason=random.choice(report_reasons),
                        created_at=fake.date_time_between(start_date=review.created_at, end_date='now', tzinfo=timezone.get_current_timezone())
                    )
            except:
                pass
