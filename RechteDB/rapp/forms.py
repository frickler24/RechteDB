from django import forms
from .models import TblUserIDundName, TblUserhatrolle, hole_organisationen

class ShowUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


class ImportForm(forms.Form):
	# Die ersten Parameter, die für einen CSV-Import abgefragt werden müssen
	organisation = forms.ChoiceField(label='Organisation')
	datei = forms.FileField(label = 'Dateiname')

	def __init__(self, *args, **kwargs):
		super(ImportForm, self).__init__(*args, **kwargs)
		self.fields['organisation'].choices = hole_organisationen()


class ImportForm_schritt3(forms.Form):
	# Der Abschluss des zweiten Schritts besteht ebenfalls nur aus einer Bestätigung,
	# deshalb sind auch hier keine Datenfelder angegeben
	# (Eventuell kann hier noch ein Flag angegeben werden, ob Doppeleinträge gesucht wertden sollen)
	doppelte_suchen = forms.BooleanField(label = 'Suche nach doppelten Einträgen (optional)', required = False)
