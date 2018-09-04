from django import forms
from .models import TblGesamt, TblUserhatrolle, TblRollen, TblRollehataf


class ShowGesamtForm(forms.ModelForm):
    pagesize = forms.CharField(max_length=5, required=False, label='Zeilen pro Seite')

    class Meta:
        model = TblGesamt
        fields = ['id', 'tf', 'enthalten_in_af', 'gf', 'pagesize', ]


class ShowUhRForm(forms.ModelForm):
    pagesize = forms.CharField(max_length=5, required=False, label='Zeilen pro Seite')

    class Meta:
        model = TblUserhatrolle
        fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', 'pagesize', ]

