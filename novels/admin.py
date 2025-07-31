from django.contrib import admin
from .models import Novel, Author, Artist, Tag, NovelTag

# Register your models here.


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "artist", "created_at", "updated_at")
    search_fields = ("name", "author__name", "artist__name")
    list_filter = ("author", "artist")
    ordering = ("-created_at",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "pen_name", "country", "created_at")
    search_fields = ("name", "pen_name")
    ordering = ("name",)
    list_filter = ("country",)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "pen_name", "country", "created_at")
    search_fields = ("name", "pen_name")
    ordering = ("name",)
    list_filter = ("country",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(NovelTag)
class NovelTagAdmin(admin.ModelAdmin):
    list_display = ("novel", "tag")
    search_fields = ("novel__name", "tag__name")
    ordering = ("novel", "tag")
    list_filter = ("tag",)
