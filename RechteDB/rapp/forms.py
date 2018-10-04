from django import forms
from .models import TblUserIDundName, TblUserhatrolle


class ShowUhRForm(forms.ModelForm):
    class Meta:
        model = TblUserhatrolle
        fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

class ImportFormx(forms.ModelForm):
    class Meta:
        model = TblUserIDundName
        fields = ['userid', 'zi_organisation', ]

class ImportForm(forms.Form):
    organisation = forms.ChoiceField(label='Organisation', )
    datei = forms.FileField(label = 'Dateiname')
