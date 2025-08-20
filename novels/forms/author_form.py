from django import forms
from novels.models import Author
from django.utils.translation import gettext_lazy as _

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'pen_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pen_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']

        # Nếu đang chỉnh sửa (tức là self.instance đã có id)
        if Author.objects.exclude(id=self.instance.id).filter(name=name).exists(): 
            raise forms.ValidationError(_("Tác giả này đã tồn tại."))

        return name
