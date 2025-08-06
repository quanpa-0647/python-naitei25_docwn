from enum import Enum


class UserRole(Enum):
    GUEST = "g"
    USER = "u"
    WEBSITE_ADMIN = "wa"
    SYSTEM_ADMIN = "sa"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class Gender(Enum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class ProgressStatus(Enum):
    ONGOING = "o"
    COMPLETED = "c"
    SUSPEND = "s"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class ApprovalStatus(Enum):
    DRAFT = "d"
    PENDING = "p"
    APPROVED = "a"
    REJECTED = "r"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]

START_POSITION_DEFAULT = 1
PROGRESS_DEFAULT = 0.0
COUNT_DEFAULT = 0

# Constants for max_length
MAX_USERNAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_COUNTRY_LENGTH = 100
MAX_IMAGE_URL_LENGTH = 255
MAX_TITLE_LENGTH = 255
MAX_SLUG_LENGTH = 600  # For chapter slugs combining volume and title
MAX_TYPE_LENGTH = 255
MAX_GENDER_LENGTH = 1
MAX_STATUS_LENGTH = 1
MAX_ROLE_LENGTH = 2
MAX_SESSION_REMEMBER = 1209600
MAX_RATE = 5
MAX_TOKEN_LENGTH = 255
MAX_LIMIT_CHUNKS = 5
MAX_LIKE_NOVELS =18
MAX_TREND_NOVELS =30
MAX_MOST_READ_NOVELS =30
MAX_NEW_NOVELS = 100
MAX_FINISH_NOVELS =13
MAX_NEWUPDATE_NOVELS =12
MAX_LATEST_CHAPTER = 14
MIN_LATEST_CHAPTER = 1
MAX_HOME_COMMENTS = 10  # Maximum comments to show on home page
MAX_RANDOM_STRING_LENGTH = 10 

# Constants for min_length
MIN_RATE = 0
MIN_PASSWORD_LENGTH = 8
MIN_TEXTAREA_ROWS = 3
MIN_SESSION_REMEMBER = 0

# Session
SESSION_COOKIE_AGE_SECONDS = 86400  # 24 hours

# Date
DATE_FORMAT_DMY = "d/m/Y"
DATE_FORMAT_DMYHI = "d/m/Y H:i"
DATE_FORMAT_DMY2 = "%d/%m/%Y"
# Chapter
MAX_CHAPTER_LIST = 4
MAX_CHAPTER_LIST_PLUS = 5

# Novel validation
MIN_NOVEL_NAME_LENGTH = 3
MIN_NOVEL_SUMMARY_LENGTH = 10
MAX_NOVEL_SUMMARY_LENGTH = 2000
MAX_NOVEL_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# PAGINATOR
PAGINATOR_TAG_LIST = 10  # Increased for better consistency
PAGINATOR_COMMON_LIST = 10  # Increased for better consistency
DEFAULT_PAGE_NUMBER = 1

# Allowed image types for novel uploads
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp",
]

MAX_TRUNCATED_REJECTED_REASON_LENGTH = 10
MAX_REJECTTED_REASONS_LENGTH = 1000

# Constants for pagination
NOVEL_PER_PAGE = 10
PAGINATION_PAGE_RANGE = 3  # Number of pages to show before and after current page
PAGINATION_TEMPLATE_PATH = 'admin/includes/pagination_range.html'  # Template path for pagination
PAGINATION_MIN_PAGE = 1  # Minimum page number
PAGINATION_ELLIPSIS_THRESHOLD = 2  # Page difference threshold for showing ellipsis
PAGINATION_MIN_PAGES_TO_SHOW = 1  # Minimum number of pages required to show pagination

# Chunking configuration
MAX_CHUNK_SIZE = 10000  # Maximum size for a chunk in characters

# Reading constants
WORDS_PER_MINUTE = 200  # Average reading speed for time estimation
SUMMARY_TRUNCATE_WORDS = 20  # Number of words to show in novel summary previews

# Draft constants
DEFAULT_DRAFT_NAME_PREFIX = "Draft"
DEFAULT_DRAFT_FALLBACK_NAME = "Novel"
DEFAULT_DRAFT_SUMMARY = "Draft content - to be updated later"

# Volume constants
MAX_VOLUME_NAME_LENGTH = 255

#Rating constants
DEFAULT_RATING_AVERAGE = 0.0

# Security constants
SECURE_HSTS_SECONDS_HEROKU = 31536000  # 1 year in seconds
SECURE_HSTS_SECONDS_DEVELOPMENT = 0  # No HSTS in development mode

# Time constants for relative time calculation
SECONDS_PER_HOUR = 3600  # 60 * 60
SECONDS_PER_MINUTE = 60
SEARCH_RESULTS_LIMIT = 20  # Limit for search results
COMMENT_TRUNCATE_LENGTH = 200  # Length to truncate comments

# Constants for attempting
MAX_ATTEMPTS = 10
