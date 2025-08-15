import requests
import json

from django import forms
from django.utils.translation import gettext as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.utils.text import slugify

from .utils import ChunkManager, SimpleChunker
from .models import Novel, Tag, Author, Artist, Volume, Chapter
from .api import ExternalAPIManager
from docwn import settings
from constants import (
    ApprovalStatus,
    ProgressStatus,
    MIN_NOVEL_NAME_LENGTH,
    MIN_NOVEL_SUMMARY_LENGTH,
    MAX_NOVEL_SUMMARY_LENGTH,
    MAX_NOVEL_IMAGE_SIZE,
    ALLOWED_IMAGE_TYPES,
    DEFAULT_DRAFT_NAME_PREFIX,
    DEFAULT_DRAFT_FALLBACK_NAME,
    DEFAULT_DRAFT_SUMMARY,
    MAX_VOLUME_NAME_LENGTH,
    MAX_CHUNK_SIZE
)
from accounts.models import User
from django.utils.text import slugify


class NovelForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget(
            attrs={
                "data-placeholder": _("Chọn thể loại..."),
                "data-label": _("Thể loại"),
            }
        ),
        required=False,
        label=_("Thể loại"),
        help_text=_("Chọn một hoặc nhiều thể loại cho tiểu thuyết"),
    )

    author = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Tác giả"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn tác giả..."),
                "data-label": _("Tác giả"),
                "class": "form-control",
            }
        ),
    )

    artist = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Họa sĩ"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn họa sĩ..."),
                "data-label": _("Họa sĩ"),
                "class": "form-control",
            }
        ),
    )

    upload_anonymously = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Đăng ẩn danh"),
        help_text=_(
            "Chọn để đăng tiểu thuyết mà không hiển thị tên người đăng"
        ),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "data-label": _("Đăng ẩn danh"),
                "data-placeholder": _("Chọn để đăng ẩn danh"),
            }
        ),
    )

    image_file = forms.ImageField(
        required=False,
        label=_("Ảnh bìa"),
        help_text=_("Tải lên ảnh bìa cho tiểu thuyết"),
        widget=forms.FileInput(
            attrs={
                "accept": "image/*",
                "data-label": _("Ảnh bìa"),
                "data-placeholder": _("Chọn ảnh bìa..."),
                "data-upload-text": _("Chọn ảnh từ thiết bị của bạn"),
                "data-preview-text": _("Xem trước ảnh"),
            }
        ),
    )

    progress_status = forms.ChoiceField(
        choices=[
            (ProgressStatus.ONGOING.value, _("ĐANG TIẾN HÀNH")),
            (ProgressStatus.COMPLETED.value, _("HOÀN THÀNH")),
            (ProgressStatus.SUSPEND.value, _("TẠM DỪNG")),
        ],
        required=False,
        label=_("Trạng thái tiến độ"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn trạng thái..."),
                "data-label": _("Trạng thái tiến độ"),
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Novel
        fields = ["name", "other_names", "summary"]
        labels = {
            "name": _("Tên tiểu thuyết"),
            "other_names": _("Tên khác"),
            "summary": _("Tóm tắt"),
        }
        help_texts = {
            "summary": _(
                "Viết tóm tắt ngắn gọn về nội dung tiểu thuyết "
                "(tối thiểu {min} ký tự, tối đa {max} ký tự)"
            ).format(
                min=MIN_NOVEL_SUMMARY_LENGTH, max=MAX_NOVEL_SUMMARY_LENGTH
            ),
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": _("Nhập tên tiểu thuyết"),
                    "data-placeholder": _("Nhập tên tiểu thuyết"),
                    "data-label": _("Tên tiểu thuyết"),
                    "data-required-msg": _("Tên tiểu thuyết là bắt buộc"),
                    "data-min-length-msg": _(
                        "Tên tiểu thuyết phải có ít nhất {min} ký tự"
                    ).format(min=MIN_NOVEL_NAME_LENGTH),
                }
            ),
            "other_names": forms.TextInput(
                attrs={
                    "placeholder": _("Nhập tên khác (tùy chọn)"),
                    "data-placeholder": _("Nhập tên khác (tùy chọn)"),
                    "data-label": _("Tên khác"),
                }
            ),
            "summary": forms.Textarea(
                attrs={
                    "placeholder": _("Nhập tóm tắt nội dung tiểu thuyết"),
                    "data-placeholder": _("Nhập tóm tắt nội dung tiểu thuyết"),
                    "data-label": _("Tóm tắt"),
                    "data-required-msg": _("Tóm tắt là bắt buộc"),
                    "data-min-length-msg": _(
                        "Tóm tắt phải có ít nhất {min} ký tự"
                    ).format(min=MIN_NOVEL_SUMMARY_LENGTH),
                    "data-max-length": str(MAX_NOVEL_SUMMARY_LENGTH),
                    "data-counter-template": _("{current}/{max} ký tự"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Check if user already exists as author/artist
        user_is_existing_author = False
        user_is_existing_artist = False

        if self.user:
            user_name = self.user.get_name()
            user_is_existing_author = Author.objects.filter(
                name=user_name
            ).exists()
            user_is_existing_artist = Artist.objects.filter(
                name=user_name
            ).exists()

        # Populate author choices
        author_choices = [
            ("", _("--- Chọn tác giả ---")),
            ("unknown", _("Không rõ")),
        ]

        # Only add "Me" option if user is not already an author
        if self.user and not user_is_existing_author:
            author_choices.append(("me", _("Tôi")))

        # Add existing authors (including user if they are already an author)
        for author in Author.objects.all():
            author_choices.append((f"author_{author.id}", author.name))

        self.fields["author"].choices = author_choices

        # Populate artist choices
        artist_choices = [
            ("", _("--- Chọn họa sĩ ---")),
            ("unknown", _("Không rõ")),
        ]

        # Only add "Me" option if user is not already an artist
        if self.user and not user_is_existing_artist:
            artist_choices.append(("me", _("Tôi")))

        # Add existing artists (including user if they are already an artist)
        for artist in Artist.objects.all():
            artist_choices.append((f"artist_{artist.id}", artist.name))

        self.fields["artist"].choices = artist_choices

    def clean(self):
        cleaned_data = super().clean()

        # Check if this is a draft save (less strict validation)
        is_draft = (
            hasattr(self, "request")
            and self.request
            and self.request.POST.get("save_as_draft", False)
        )

        if not is_draft:
            # Full validation for non-draft submissions
            name = cleaned_data.get("name")
            summary = cleaned_data.get("summary")

            if not name or not name.strip():
                raise forms.ValidationError(
                    _("Tên tiểu thuyết là bắt buộc khi xuất bản.")
                )

            if not summary or not summary.strip():
                raise forms.ValidationError(
                    _("Tóm tắt là bắt buộc khi xuất bản.")
                )

            if len(name.strip()) < MIN_NOVEL_NAME_LENGTH:
                raise forms.ValidationError(
                    _("Tên tiểu thuyết phải có ít nhất {min} ký tự.").format(
                        min=MIN_NOVEL_NAME_LENGTH
                    )
                )

            if len(summary.strip()) < MIN_NOVEL_SUMMARY_LENGTH:
                raise forms.ValidationError(
                    _("Tóm tắt phải có ít nhất {min} ký tự.").format(
                        min=MIN_NOVEL_SUMMARY_LENGTH
                    )
                )

        return cleaned_data

    def clean_author(self):
        author = self.cleaned_data.get("author")
        # Allow empty, "unknown", "me", or valid author IDs
        if author and author not in ["", "unknown", "me"]:
            if not author.startswith("author_"):
                raise forms.ValidationError(_("Lựa chọn tác giả không hợp lệ."))
            try:
                author_id = int(author.replace("author_", ""))
                if not Author.objects.filter(id=author_id).exists():
                    raise forms.ValidationError(_("Tác giả được chọn không tồn tại."))
            except ValueError:
                raise forms.ValidationError(_("Lựa chọn tác giả không hợp lệ."))
        return author

    def clean_artist(self):
        artist = self.cleaned_data.get("artist")
        # Allow empty, "unknown", "me", or valid artist IDs
        if artist and artist not in ["", "unknown", "me"]:
            if not artist.startswith("artist_"):
                raise forms.ValidationError(_("Lựa chọn họa sĩ không hợp lệ."))
            try:
                artist_id = int(artist.replace("artist_", ""))
                if not Artist.objects.filter(id=artist_id).exists():
                    raise forms.ValidationError(_("Họa sĩ được chọn không tồn tại."))
            except ValueError:
                raise forms.ValidationError(_("Lựa chọn họa sĩ không hợp lệ."))
        return artist

    def clean_image_file(self):
        image = self.cleaned_data.get("image_file")
        if image:
            # Check file size
            if image.size > MAX_NOVEL_IMAGE_SIZE:
                max_size_mb = MAX_NOVEL_IMAGE_SIZE // (1024 * 1024)
                raise forms.ValidationError(
                    _("Kích thước file phải nhỏ hơn {max}MB.").format(
                        max=max_size_mb
                    )
                )

            # Check file type
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError(
                    _("Chỉ chấp nhận file ảnh (JPEG, PNG, GIF, WebP).")
                )

        return image

    def upload_to_imgbb(self, image):
        """Upload image using external API manager"""
        return ExternalAPIManager.upload_image(image)

    def save(self, commit=True):
        novel = super().save(commit=False)
        
        # Check if this is a draft save
        is_draft = (
            hasattr(self, "request")
            and self.request
            and self.request.POST.get("save_as_draft", False)
        )
        
        # Handle empty name for drafts
        if is_draft and (not novel.name or not novel.name.strip()):
            novel.name = f"{DEFAULT_DRAFT_NAME_PREFIX} {self.user.get_name() if self.user else DEFAULT_DRAFT_FALLBACK_NAME}"
            
        # Handle empty summary for drafts
        if is_draft and (not novel.summary or not novel.summary.strip()):
            novel.summary = DEFAULT_DRAFT_SUMMARY
            
        # Set progress status if not provided
        progress_status = self.cleaned_data.get("progress_status")
        if progress_status:
            novel.progress_status = progress_status
        else:
            # Set default progress status from constants
            novel.progress_status = ProgressStatus.ONGOING.value

        # Handle author selection
        author_choice = self.cleaned_data.get("author")
        if not author_choice or author_choice == "unknown":
            # Empty choice or Unknown author -> set to null
            novel.author = None
        elif author_choice == "me" and self.user:
            # Create or get Author record for the user
            author, created = Author.objects.get_or_create(
                name=self.user.get_name(),
                defaults={"description": f"Tác giả: {self.user.get_name()}"},
            )
            novel.author = author
        elif author_choice and author_choice.startswith("author_"):
            # Existing author selected
            author_id = author_choice.replace("author_", "")
            try:
                author = Author.objects.get(id=int(author_id))
                novel.author = author
            except (Author.DoesNotExist, ValueError):
                novel.author = None

        # Handle artist selection
        artist_choice = self.cleaned_data.get("artist")
        if not artist_choice or artist_choice == "unknown":
            # Empty choice or Unknown artist -> set to null
            novel.artist = None
        elif artist_choice == "me" and self.user:
            # Create or get Artist record for the user
            artist, created = Artist.objects.get_or_create(
                name=self.user.get_name(),
                defaults={"description": f"Họa sĩ: {self.user.get_name()}"},
            )
            novel.artist = artist
        elif artist_choice and artist_choice.startswith("artist_"):
            # Existing artist selected
            artist_id = artist_choice.replace("artist_", "")
            try:
                artist = Artist.objects.get(id=int(artist_id))
                novel.artist = artist
            except (Artist.DoesNotExist, ValueError):
                novel.artist = None

        # Handle image upload
        image = self.cleaned_data.get("image_file")
        if image:
            image_url = self.upload_to_imgbb(image)
            if image_url:
                novel.image_url = image_url
            # If upload fails, continue without image

        if commit:
            novel.save()
            self.save_m2m()
        return novel

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        slug = slugify(name)

        # Nếu đang chỉnh sửa (tức là self.instance đã có id)
        if Tag.objects.exclude(id=self.instance.id).filter(slug=slug).exists():
            raise forms.ValidationError(_("Tag với tên này đã tồn tại."))

        return name



    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance



class ChapterForm(forms.ModelForm):
    """Form for adding new chapters"""
    
    # Choice field for selecting existing volume or creating new one
    volume_choice = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Chọn Volume"),
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    
    # Field for creating new volume
    new_volume_name = forms.CharField(
        max_length=MAX_VOLUME_NAME_LENGTH,
        required=False,
        label=_("Tên Volume mới"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Nhập tên volume mới..."),
            }
        ),
        help_text=_("Chap mới sẽ được thêm vào volume mới này")
    )
    
    # Chapter content field
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 15,
                "placeholder": _("Nhập nội dung chapter...")
            }
        ),
        label=_("Nội dung"),
    )

    class Meta:
        model = Chapter
        fields = ['title']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Nhập tiêu đề chapter..."),
                }
            ),
        }
        labels = {
            'title': _("Tiêu đề Chapter"),
        }

    def __init__(self, novel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.novel = novel
        
        if novel:
            # Get existing volumes for this novel
            volumes = Volume.objects.filter(novel=novel).order_by('position')
            volume_choices = [('', _('-- Chọn Volume --'))]
            volume_choices.extend([(vol.id, vol.name) for vol in volumes])
            volume_choices.append(('new', _('Tạo Volume mới')))
            
            self.fields['volume_choice'].choices = volume_choices

    def clean_new_volume_name(self):
        new_volume_name = self.cleaned_data.get('new_volume_name')
        volume_choice = self.cleaned_data.get('volume_choice')
        
        if volume_choice == 'new' and new_volume_name and self.novel:
            # Check if volume name already exists in this novel
            if Volume.objects.filter(novel=self.novel, name=new_volume_name).exists():
                raise forms.ValidationError(_("Tên volume đã tồn tại trong tiểu thuyết này"))
        
        return new_volume_name

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError(_("Tiêu đề chapter là bắt buộc"))
        return title.strip()

    def clean(self):
        cleaned_data = super().clean()
        volume_choice = cleaned_data.get('volume_choice')
        new_volume_name = cleaned_data.get('new_volume_name')
        title = cleaned_data.get('title')
        
        if not volume_choice:
            raise forms.ValidationError(_("Vui lòng chọn volume hoặc tạo volume mới"))
        
        if volume_choice == 'new' and not new_volume_name:
            raise forms.ValidationError(_("Vui lòng nhập tên volume mới"))
        
        if volume_choice != 'new' and volume_choice and new_volume_name:
            raise forms.ValidationError(_("Không thể vừa chọn volume có sẵn vừa tạo volume mới"))
        
        # Check for duplicate volume name when creating new volume
        if volume_choice == 'new' and new_volume_name and self.novel:
            if Volume.objects.filter(novel=self.novel, name=new_volume_name).exists():
                raise forms.ValidationError(_("Tên volume đã tồn tại trong tiểu thuyết này"))
        
        # Check for duplicate chapter title within the selected volume
        if title and self.novel:
            if volume_choice == 'new' and new_volume_name:
                # For new volume, check if the combination of volume name + chapter title
                # would create a duplicate slug
                volume_slug = slugify(new_volume_name)
                chapter_slug = slugify(title)
                
                # Check if any existing chapter would have the same slug pattern
                existing_chapters = Chapter.objects.filter(
                    volume__novel=self.novel,
                    deleted_at__isnull=True
                )
                
                for existing_chapter in existing_chapters:
                    existing_volume_slug = slugify(existing_chapter.volume.name)
                    existing_chapter_slug = slugify(existing_chapter.title)
                    
                    if (existing_volume_slug == volume_slug and 
                        existing_chapter_slug == chapter_slug):
                        raise forms.ValidationError(
                            _("Kết hợp tên volume và tiêu đề chapter này sẽ tạo ra slug trùng lặp")
                        )
                        
            elif volume_choice and volume_choice != 'new':
                # For existing volume, check within that specific volume
                try:
                    volume = Volume.objects.get(id=volume_choice, novel=self.novel)
                    existing_chapters = Chapter.objects.filter(
                        volume=volume,
                        title=title,
                        deleted_at__isnull=True
                    )
                    if existing_chapters.exists():
                        raise forms.ValidationError(_("Tiêu đề chapter đã tồn tại trong volume này"))
                except Volume.DoesNotExist:
                    raise forms.ValidationError(_("Volume được chọn không hợp lệ"))
            
        return cleaned_data

    def save(self, commit=True):
        chapter = super().save(commit=False)
        
        if not self.novel:
            raise ValueError("Novel must be provided")
            
        volume_choice = self.cleaned_data.get('volume_choice')
        new_volume_name = self.cleaned_data.get('new_volume_name')
        content = self.cleaned_data.get('content')
        
        # Handle volume selection or creation
        if volume_choice == 'new':
            # Create new volume
            last_volume = Volume.objects.filter(novel=self.novel).order_by('-position').first()
            next_position = (last_volume.position + 1) if last_volume else 1
            
            volume = Volume.objects.create(
                novel=self.novel,
                name=new_volume_name,
                position=next_position
            )
        else:
            # Use existing volume
            volume = Volume.objects.get(id=volume_choice, novel=self.novel)
        
        chapter.volume = volume
        
        # Set chapter position
        last_chapter = Chapter.objects.filter(volume=volume).order_by('-position').first()
        chapter.position = (last_chapter.position + 1) if last_chapter else 1
        
        # Note: slug will be generated automatically by the model's save method
        # which includes volume information to prevent conflicts
        
        if commit:
            chapter.save()
            
            # Use normal chunking to create chunks
            # Create simple chunker with database limit
            chunker = SimpleChunker(max_chunk_size=MAX_CHUNK_SIZE)  # Database TEXT field limit
            
            # Create chunks using normal chunking
            chunk_count = ChunkManager.create_normal_chunks_for_chapter(
                chapter=chapter,
                content=content,
                chunker=chunker
            )
            
            # Note: chapter.word_count is updated automatically by ChunkManager
        
        return chapter
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'pen_name']

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'pen_name']

