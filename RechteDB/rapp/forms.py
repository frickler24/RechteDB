from django import forms
from .models import TblUserIDundName, TblUserhatrolle, hole_organisationen

class ShowUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


class ImportForm(forms.Form):
	organisation = forms.ChoiceField(label='Organisation')
	datei = forms.FileField(label = 'Dateiname')

	def __init__(self, *args, **kwargs):
		super(ImportForm, self).__init__(*args, **kwargs)
		self.fields['organisation'].choices = hole_organisationen()

