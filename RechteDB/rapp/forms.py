from django import forms
from .models import TblGesamt, TblUserhatrolle, TblRollen, TblRollehataf


class ShowUhRForm(forms.ModelForm):
    class Meta:
        model = TblUserhatrolle
        fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

