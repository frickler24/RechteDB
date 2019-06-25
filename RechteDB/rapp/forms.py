from django import forms
from .models import TblUserhatrolle, hole_organisationen

# Das hätte man auch einfacher haben können, indem die relevanten Infos in views.py eingetragen worden wären
class ShowUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


# Hier ist das anders, weil zwei Methoden zur Klasse hinzugekommen sind
# Initialisiere das Input Formular für neue Rolleneinträge mit der UserID
class CreateUhRForm(forms.ModelForm):
	userid = "Keine ID"

	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

	def __init__(self, *args, **kwargs):

		print ('kwargs in CreateUhRForm:')
		for k in kwargs:
			print (k, '->', kwargs[k])
		print ('-------------')

		self.userid = kwargs.pop('userid', None)
		self.rollenname = kwargs.pop('rollenname', 'blabla')
		super(CreateUhRForm, self).__init__(*args, **kwargs)

		# assign the default userID to the choice field
		self.initial['userid'] = self.userid
		self.initial['rollennamme'] = self.rollenname


#Auch hier ist das Thema das Initialisieren des Organisations-Choicefields
class ImportForm(forms.Form):
	# Die ersten Parameter, die für einen CSV-Import abgefragt werden müssen
	organisation = forms.ChoiceField(label='Organisation')
	datei = forms.FileField(label = 'Dateiname')

	def __init__(self, *args, **kwargs):
		super(ImportForm, self).__init__(*args, **kwargs)
		self.fields['organisation'].choices = hole_organisationen()

# Das hier behandelte boolean Field ist nicht Inhalt des Models, sondern ändert lediglich den Workflow
class ImportForm_schritt3(forms.Form):
	# Der Abschluss des zweiten Schritts besteht ebenfalls nur aus einer Bestätigung,
	# deshalb sind auch hier keine Datenfelder angegeben
	# (Eventuell kann hier noch ein Flag angegeben werden, ob Doppeleinträge gesucht wertden sollen)
	doppelte_suchen = forms.BooleanField(label = 'Suche nach doppelten Einträgen (optional)', required = False)
