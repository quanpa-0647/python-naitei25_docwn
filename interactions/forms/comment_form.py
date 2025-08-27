# interactions/forms.py
from django import forms
from interactions.models import Comment
from django.utils.translation import gettext_lazy as _
from constants import TEXTAREA_ROWS, MAX_COMMENT_LENGTH

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': TEXTAREA_ROWS,
                'placeholder':  _('Viết bình luận...')
            }),
        max_length=MAX_COMMENT_LENGTH
    )

    class Meta:
        model = Comment
        fields = ['content']
