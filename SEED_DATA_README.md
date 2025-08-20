# Seed Data Management Commands

This project includes three powerful Django management commands for handling seed data in your novel publishing platform.

## Available Commands

### 1. `seed_data` - Generate Seed Data

Generates comprehensive seed data including users, authors, artists, novels, chapters, comments, and reviews.

#### Basic Usage
```bash
python manage.py seed_data
```

#### Advanced Usage with Options
```bash
python manage.py seed_data \
    --users 20 \
    --authors 15 \
    --artists 10 \
    --tags 25 \
    --novels 30 \
    --volumes-per-novel 3 \
    --chapters-per-volume 10 \
    --comments 100 \
    --reviews 50 \
    --with-content
```

#### Available Options
- `--users N`: Number of users to create (default: 20)
- `--authors N`: Number of authors to create (default: 15)
- `--artists N`: Number of artists to create (default: 10)
- `--tags N`: Number of tags to create (default: 25)
- `--novels N`: Number of novels to create (default: 30)
- `--volumes-per-novel N`: Average volumes per novel (default: 3)
- `--chapters-per-volume N`: Average chapters per volume (default: 10)
- `--comments N`: Number of comments to create (default: 100)
- `--reviews N`: Number of reviews to create (default: 50)
- `--with-content`: Generate realistic HTML content for chapters (takes longer)

#### What Gets Created
- **Users**: Random users with profiles, including different roles
- **Authors**: Authors with biographical information
- **Artists**: Artists for novel illustrations
- **Tags**: Genre and category tags
- **Novels**: Novels with metadata, linked to authors/artists/tags
- **Volumes**: Organized chapters in volumes
- **Chapters**: Individual chapters with HTML content (if --with-content)
- **Comments**: User comments on novels (including replies)
- **Reviews**: Star ratings with review text

---

### 2. `clear_seed_data` - Clear Seed Data

Safely removes all seed data while preserving important accounts.

#### Basic Usage (with confirmation prompt)
```bash
python manage.py clear_seed_data
```

#### Skip Confirmation
```bash
python manage.py clear_seed_data --confirm
```

#### Advanced Options
```bash
# Keep admin accounts (default behavior)
python manage.py clear_seed_data --confirm --keep-admin

# DELETE EVERYTHING including admins (dangerous!)
python manage.py clear_seed_data --confirm --nuclear
```

#### Available Options
- `--confirm`: Skip the confirmation prompt
- `--keep-admin`: Keep admin/superuser accounts (default)
- `--nuclear`: **DANGEROUS** - Delete ALL data including admin accounts

#### What Gets Deleted
By default (safe mode):
- All novels, volumes, chapters, and chunks
- All comments, reviews, notifications, and reports  
- All authors, artists, and tags
- All regular user accounts (keeps superusers)

With `--nuclear` flag:
- **EVERYTHING** including admin accounts

---

### 3. `show_data` - Display Database Statistics

Shows comprehensive statistics about your database content.

#### Basic Usage
```bash
python manage.py show_data
```

#### Detailed View with Sample Data
```bash
python manage.py show_data --detailed --samples 10
```

#### Available Options
- `--detailed`: Show detailed statistics and sample records
- `--samples N`: Number of sample records to display (default: 5)

#### What Gets Displayed
- **Record Counts**: Total count for each model
- **User Statistics**: User roles, activity status, profile completion
- **Novel Statistics**: Approval status, progress status, popular tags
- **Interaction Statistics**: Comment/review activity, rating distributions
- **Sample Data**: (with --detailed) Example records from each table

---

## Example Workflows

### Quick Test Setup
```bash
# Generate minimal test data
python manage.py seed_data --users 5 --novels 3 --authors 2

# View what was created
python manage.py show_data --detailed

# Clean up when done
python manage.py clear_seed_data --confirm
```

### Full Development Environment
```bash
# Generate comprehensive data for development
python manage.py seed_data \
    --users 50 \
    --authors 25 \
    --novels 100 \
    --with-content

# Check statistics
python manage.py show_data
```

### Production-Like Data
```bash
# Generate large dataset with realistic content
python manage.py seed_data \
    --users 200 \
    --authors 50 \
    --artists 30 \
    --novels 500 \
    --volumes-per-novel 5 \
    --chapters-per-volume 15 \
    --comments 2000 \
    --reviews 800 \
    --with-content
```

---

## Safety Features

### Data Protection
- Clear command preserves superuser accounts by default
- Confirmation prompts prevent accidental deletion
- Foreign key constraints handled automatically
- Database sequences reset after clearing

### Error Handling
- Unique constraint violations handled gracefully
- Existing data won't cause conflicts
- Detailed error messages for troubleshooting
- Transaction rollback on failures

---

## Dependencies

The seed data commands require:
- `faker` - For generating realistic fake data
- `django-tinymce` - For rich text content (if using --with-content)
- `beautifulsoup4` - For HTML processing

Install with:
```bash
pip install faker django-tinymce beautifulsoup4
```

---

## Notes

### Performance
- Without `--with-content`: Very fast, suitable for CI/testing
- With `--with-content`: Slower due to HTML processing and chunking
- Large datasets may take several minutes to generate

### Rich Text Content
When using `--with-content`, chapters will include:
- Formatted HTML with paragraphs, headings, emphasis
- Proper chunking for reading pagination
- Realistic content structure

### Database Compatibility
- Optimized for MySQL (used in production)
- Also works with SQLite (for development)
- Foreign key handling database-specific
