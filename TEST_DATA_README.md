# Test Data Generation for DocWn Novel Website

This document describes the comprehensive test data that has been generated for your Django novel reading website.

## Generated Management Commands

### 1. `generate_test_data` - Comprehensive Data Generation
```bash
python manage.py generate_test_data --users 25 --authors 10 --artists 8 --tags 15 --novels 30
```

**Options:**
- `--users`: Number of users to create (default: 50)
- `--authors`: Number of authors to create (default: 25)  
- `--artists`: Number of artists to create (default: 20)
- `--tags`: Number of tags to create (default: 30)
- `--novels`: Number of novels to create (default: 100)
- `--clear`: Clear all existing data before generating new data

**Generated Data:**
- Users with different roles (regular users, website admins)
- User profiles with display names, descriptions, interests
- Authors (famous Vietnamese & international authors + random)
- Artists for novel illustrations
- Genre tags (Romance, Action, Horror, Fantasy, etc.)
- Novels with rich metadata (ratings, views, favorites, word counts)
- Novel-tag relationships
- Volumes (1-5 per novel)
- Chapters (5-20 per volume)
- Content chunks (3-10 per chapter with realistic Vietnamese content)
- User interactions (favorites, reading history, comments, reviews)
- Notifications
- Reports for inappropriate content

### 2. `generate_quick_data` - Focused Dataset
```bash
python manage.py generate_quick_data
```

Creates a smaller, focused dataset perfect for quick testing:
- 1 admin + 5 test users
- 5 famous authors and 3 artists
- 10 popular genre tags
- 8 sample novels with Vietnamese titles
- Complete volume/chapter/chunk structure
- Sample interactions

### 3. `show_stats` - Database Statistics
```bash
python manage.py show_stats
```

Shows comprehensive database statistics including:
- User counts by role and status
- Content statistics (authors, novels, chapters, etc.)
- Novel metrics (ratings, views, word counts)
- Interaction statistics (comments, reviews, notifications)
- Top active users

### 4. `show_test_data` - Sample Data Preview
```bash
python manage.py show_test_data
```

Displays sample data and test login credentials for easy access.

### 5. `clear_test_data` - Data Cleanup
```bash
python manage.py clear_test_data --confirm
```

Safely removes all test data from the database.

### 6. `fix_chunk_content` - Content Formatting Fix
```bash
python manage.py fix_chunk_content
```

Fixes chunk content formatting by converting literal `\n` characters to actual newlines for proper display in templates.

### 7. `fix_chapter_slugs` - Slug Generation Fix
```bash
python manage.py fix_chapter_slugs
```

Generates slugs for chapters that have empty slug fields, fixing URL routing issues.

## Current Database Statistics

After running the comprehensive data generation:

**Users**: 32 total
- 22 regular users
- 10 website admins
- 15 verified users

**Content**: 
- 17 authors
- 20 artists  
- 27 tags
- 77 novels
- 108 volumes
- 1,100 chapters
- 6,795 content chunks

**Novels**:
- 37 ongoing, 22 completed, 18 suspended
- 23 approved, 30 pending, 12 drafts, 12 rejected
- Average rating: 2.96/5
- Total views: 728,012
- Total words: 7,754,330

**Interactions**:
- 392 comments (including 80 replies)
- 189 reviews
- 130 favorites
- 457 reading history entries
- 150 notifications
- 29 reports

## Test Login Credentials

### Admin User
- **Email**: testadmin@docwn.com
- **Username**: testadmin
- **Password**: admin123
- **Role**: Website Admin

### Regular Test Users
- **Email**: user1@test.com | **Username**: testuser1 | **Password**: password123
- **Email**: user2@test.com | **Username**: testuser2 | **Password**: password123
- **Email**: testuser1000@example.com | **Username**: testuser1000 | **Password**: password123

## Features You Can Now Test

✅ **User Management**
- User registration and login
- Different user roles and permissions
- User profiles and settings
- Email verification system

✅ **Novel Management**
- Novel creation, editing, and publishing
- Volume and chapter organization
- Content approval workflow
- Rich text content with chunks

✅ **Reading Experience**
- Novel browsing and discovery
- Chapter reading with progress tracking
- Reading history
- Bookmarks and favorites

✅ **Interaction Features**
- Comments and replies
- Rating and review system
- User notifications
- Content reporting system

✅ **Search & Discovery**
- Novel search and filtering
- Tag-based categorization
- Trending and popular novels
- Author and artist pages

✅ **Admin Features**
- Content moderation
- User management
- Novel approval/rejection
- Statistics and analytics

## Content Diversity

The generated data includes:

**Novel Genres**: Romance, Action, Horror, Fantasy, School Life, Isekai, Sci-Fi, Mystery, Comedy, Slice of Life

**Novel Types**: 
- Vietnamese literature classics
- Modern romance stories
- Fantasy adventures
- School-based stories
- Isekai/reincarnation tales
- Sci-fi epics
- Mystery thrillers

**Realistic Content**: All novels have Vietnamese titles and summaries, with content chunks containing realistic Vietnamese story excerpts that flow naturally.

**User Diversity**: Users have Vietnamese names and authentic profile information, with varied interests and reading patterns.

## Data Relationships

The test data maintains proper database relationships:
- Novels → Authors/Artists (many-to-one)
- Novels → Tags (many-to-many through NovelTag)
- Novels → Volumes → Chapters → Chunks (hierarchical)
- Users → Reading History, Favorites, Comments, Reviews (one-to-many)
- Comments → Replies (self-referential)

This comprehensive test dataset allows you to thoroughly test all features of your novel reading website with realistic, diverse, and properly structured data.
