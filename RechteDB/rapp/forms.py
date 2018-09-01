from django import forms
from .models import TblGesamt

class ShowGesamtForm(forms.ModelForm):

    class Meta:
        model = TblGesamt
        fields = ['id', 'tf', 'enthalten_in_af', 'gf', ]
