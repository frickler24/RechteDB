from django import forms
from .models import TblUserhatrolle, hole_organisationen
from urllib.parse import quote, unquote


# Das hätte man auch einfacher haben können, indem die relevanten Infos in views.py eingetragen worden wären
class ShowUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


# Hier ist das anders, weil eine Methode zur Klasse hinzugekommen ist:
# Initialisiere das Input Formular für neue Rolleneinträge mit der UserID, dem Modell und der Zuständigkeitsstufe
class CreateUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

	def __init__(self, *args, **kwargs):
		"""
		Hole die 3 Parameter, die von der ReST-Schnittstelle übergeben wurden und fülle damit eine initial-Struktur.
		Damit werden die drei Werte Userid, Rollenname und Schweerpunkt/Vertretung initialisiert angezeigt.
		:param args:
		:param kwargs: Das Wesentliche steht hier drin

		print ('kwargs in CreateUhRForm:')
		for k in kwargs:
			print (k, '->', kwargs[k])
		print ('-------------')
		"""

		self.userid = kwargs.pop('userid', None)[:7].upper()
		self.rollenname = unquote(kwargs.pop('rollenname', 'Spielrolle'))
		self.schwerpunkt_vertretung = kwargs.pop('schwerpunkt_vertretung', 'Schwerpunkt')
		super(CreateUhRForm, self).__init__(*args, **kwargs)

		# print ('CreateUhRForm(__init__):', self.userid, self.rollenname, self.schwerpunkt_vertretung)
		self.initial['userid'] = self.userid
		self.initial['rollenname'] = self.rollenname
		self.initial['schwerpunkt_vertretung'] = self.schwerpunkt_vertretung


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
