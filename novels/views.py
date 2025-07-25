from django.shortcuts import render
from django.templatetags.static import static
from .fake_data import card_list, discussion_data, comments

def Home(request):
    context = {
        'card_list': card_list,
        'discussion_data': discussion_data,
        'comments': comments
    }
    return render(request, 'novels/home.html', context)
