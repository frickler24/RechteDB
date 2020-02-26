from django import forms
from urllib.parse import quote, unquote

from .models import TblUserhatrolle
from .models import hole_organisationen
from .models import Manuelle_Berechtigung


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
        """

        self.userid = kwargs.pop('userid', None)
        if self.userid != None:
            self.userid = 'X' + self.userid[1:7].upper()
        self.rollenname = unquote(kwargs.pop('rollenname', 'Spielrolle'))
        self.schwerpunkt_vertretung = kwargs.pop('schwerpunkt_vertretung', 'Schwerpunkt')
        super(CreateUhRForm, self).__init__(*args, **kwargs)

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



# Formular für das Umbenennen von Rollen
class FormUmbenennen(forms.Form):
    alter_name = forms.CharField(max_length=50, label='Bestehender Rollenname',
        error_messages={'required': 'Bitte geben Sie den bestehenden Rollennamen an', 'invalid': 'Bestehender Rollennamen wird benötigt'})
    neuer_name = forms.CharField(max_length=50, label='Zukünftiger Rollenname',
        error_messages={'required': 'Bitte geben Sie den zukünftigen Rollennamen an', 'invalid': 'Zukünftiger Rollennamen wird benötigt'})
