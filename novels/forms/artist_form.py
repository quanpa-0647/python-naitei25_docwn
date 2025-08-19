from django import forms
from novels.models import Artist
from django.utils.translation import gettext_lazy as _

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'pen_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pen_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']

        # Nếu đang chỉnh sửa (tức là self.instance đã có id)
        if Artist.objects.exclude(id=self.instance.id).filter(name=name).exists(): 
            raise forms.ValidationError(_("Họa sĩ này đã tồn tại."))

        return name

