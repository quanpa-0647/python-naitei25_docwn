from django.shortcuts import render
from django.templatetags.static import static
from .fake_data import card_list, discussion_data, comments
from django.shortcuts import get_object_or_404
from .models import Novel, Tag, Volume
from constants import (
    DATE_FORMAT_DMY,
    MAX_CHAPTER_LIST
)

def Home(request):
    context = {
        'card_list': card_list,
        'discussion_data': discussion_data,
        'comments': comments
    }
    return render(request, 'novels/home.html', context)

def novel_detail(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id)
    tags = Tag.objects.filter(noveltag__novel=novel)
    volumes = Volume.objects.filter(
        novel=novel).prefetch_related('chapters')
    
    for volume in volumes:
        volume.chapter_list = list(volume.chapters.all())
        volume.remaining_chapters = max(len(volume.chapter_list) - MAX_CHAPTER_LIST, 0)

    context = {
        'novel': novel,
        'tags': tags,
        'volumes': volumes,
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'MAX_CHAPTER_LIST': MAX_CHAPTER_LIST
    }
    return render(request, 'novels/novel_detail.html', context)

