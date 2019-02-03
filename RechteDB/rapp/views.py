# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Create your views here.

from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django import forms

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Zum Einlesen der csv
import csv, textwrap, re, subprocess, os

from .filters import PanelFilter, UseridFilter
from .forms import ShowUhRForm, CreateUhRForm, ImportForm, ImportForm_schritt3
from .models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform, TblUserhatrolle, \
					Tblrechteneuvonimport, Tblrechteamneu
from .xhtml2 import render_to_pdf

# An dieser stelle stehen diverse Tools zum Aufsetzen der Datenbank mit SPs
from .stored_procedures import *

###################################################################
# RApp - erforderliche Sichten und Reports

# ToDo: Alle Rollen sowie die daran hängenden AF für eine Selektion (gruppiert für PDF)
# ToDo: Alle TF / GF / AF / Rollen für selektierte User - Evtl. gibt es das schon beim jetzigen Filterpanel

# ToDo: Abgleich vorhandener Rechte selektierter User mit Zertifizierungsliste (Importfunktion für die Liste!)

# ToDo: Abgleich vorhandener Rechte mit Rollenvorgaben
# ToDo: - Was fehlt?
# ToDo: - Was ist zu viel?
# ToDo: - Jeweils aufgeteilt für XV-, jeden vorhandenen AV/BV/CV und evtl. vorhandenen DV-User

# ToDo: Welche Direktzuordnungen hat eine UID schon über vorhandene AF?
# ToDo: - Welche Zuordnung ist damit doppelt?
# ToDo: - Welche TF fehlt als zugeordnete AF?
# ToDo: - Welche bekannten AFen würden hier helfen?

# ToDo: Importfunktion für "Alle meine TFen und die zugeordneten User"
# ToDo: Importfunktion für "Alle meine AFen und die zugeordneten User"

# ToDo: Alten "Finde Datei"-Dialog implemenieren

# ToDo: Hier werden sicherlich noch etliche Filterfunktionen benötigt:
# ToDo: Was passt eventuell nicht (welche Personen passen nicht in die erlaubten Orgabereiche)
# ToDo: Welche Rechte haben Ausschluss-/Einschlusskriterien und sind sie erfüllt?
# ToDo: Welche Rechte sind redundant, weil sie neu modelliert wurden und was ist die Alternativempfehlung?
# ToDo: Zu welchen Orgabereichen (Importfunktion dafür!) gehören die identifizierten User (Vorbereitung Mail an FK zum Prüfen und eventuellem Löschen

# ToDo: Links auf die change- create- und delete-Seiten ausprobieren. Sind eigene Seiten im Frontend besser?
# ToDo: Filter-Panel mit excel Export versorgen
# ToDo: Kompakte Liste für Rolle und AF mit Filtermöglichkeit und PDF Generierung

# ToDo: Die gesamten Modellnamen können mal überarbeitet werden (kein TBL am Anfang etc.)

# ToDo: Die tables alternierend einfärben
# ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller userids benötigt wird, sonst in SP löschen nach Nutzung
# ToDO: Längenbegrenzungen checken in Modell für UserHatRolle

# ToDo: Neuanlage von Rollen in mehreren Zeilen vorbereiten?
# ToDo: Suche: Wo kann man die Modelle anpassen? Braucht das Ändern der Modellzugehörigkeit noch jemand, oder ist das mit dem neuen Rollenmodell obsolet?
# ToDo: Userrolle: Link von der Rollensicht auf tbluseridundname im Admin

def get_version(package):
	"""
	Return package version as listed in `__version__` in `init.py`.
	"""
	init_py = open(os.path.join(package, '__init__.py')).read()
	manual = re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
	git_rev = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
	return manual + ' - ' + git_rev.decode('utf-8')

version = get_version('rapp')


# Der Direkteinsteig für die gesamte Anwendung
# Dies ist die Einstiegsseite, sie ist ohne Login erreichbar.
def home(request):
	"""
	Zeige ein paar Statistik-Infos über die RechteDB.
	Das stellt sicher, dass die Anbidnung an die Datenbank funzt
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	num_rights = TblGesamt.objects.all().count()
	num_userids = TblUserIDundName.objects.all().count
	num_active_userids = TblUserIDundName.objects.filter(geloescht=False).count
	num_plattforms = TblPlattform.objects.count
	num_iamba = TblGesamt.objects.filter(geloescht=False,
										 userid_name__abteilung__icontains='ZI-AI-BA',
										 userid_name__geloescht=False).count
	num_userids_in_department = TblUserIDundName.objects.filter(geloescht=False, abteilung__icontains='ZI-AI-BA').count
	num_teams = TblOrga.objects.all().count
	num_active_rights = TblGesamt.objects.filter(geloescht=False).count

	# Sicherheitshalber wird immer bei Aufruf der Startseite die Tabelle tbl_AFListe neu aufgebaut
	with connection.cursor() as cursor:
		try:
			cursor.callproc("erzeuge_af_liste")  # diese SProc benötigt die Orga nicht als Parameter
		except:
			e = sys.exc_info()[0]
			fehler = format("Error: %s" % e)
			print('Fehler Beim Erstellen der AFListe, StoredProc erzeuge_af_liste', fehler)

		cursor.close()

	request.session['version'] = version

	return render(
		request,
		'index.html',
		context={
			'num_rights': num_rights,
			'num_active_rights': num_active_rights,
			'num_userIDs': num_userids,
			'num_iam_ba': num_iamba,
			'num_activeUserIDs': num_active_userids,
			'num_plattforms': num_plattforms,
			'num_userIDsInDepartment': num_userids_in_department,
			'num_teams': num_teams,
			'num_users': User.objects.all().count,
		},
	)

###################################################################
# Gesamtliste
class GesamtListView(LoginRequiredMixin, ListView):
	"""Die Gesamtliste der Rechte ungefiltert"""
	model = TblGesamt
	paginate_by = 50

class GesamtDetailView(LoginRequiredMixin, generic.DetailView):
	"""Die Detailsicht eines einzelnen Rechts"""
	model = TblGesamt


###################################################################
# Rechte-User (Gemeint sind nicht die Anwender der RechteDB!)
class UserIDundNameListView(LoginRequiredMixin, ListView):
	"""Die Gesamtliste der User ungefiltert"""
	model = TblUserIDundName
	paginate_by = 50
class TblUserIDundNameCreate(LoginRequiredMixin, CreateView):
	"""Erstellen eines neuen Users"""
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblUserIDundNameUpdate(LoginRequiredMixin, UpdateView):
	"""Ändern eines Users"""
	model = TblUserIDundName
	fields = '__all__'
class TblUserIDundNameDelete(LoginRequiredMixin, DeleteView):
	"""Löschen eines Users"""
	model = TblUserIDundName
	success_url = reverse_lazy('userliste')

@login_required
def userToggleGeloescht(request, pk):
	"""
	View function zum Togglen des Gelöscht-Flags in der DB für eine konkrete Instanz.
	Dieser Aufruf wird nicht in zwei Schritten als GET / POST-Kombination durchgeführt.
	sondern ausschließlich als GET.
	:param request: GET oder POST Request vom Browser
	:param pk: ID des zu löschenden UserID-Eintrags
	:return: Gerendertes HTML
	"""
	user_inst = get_object_or_404(TblUserIDundName, pk = pk)

	user_inst.geloescht = not user_inst.geloescht
	user_inst.save()

	# redirect to a new URL:
	return HttpResponseRedirect(reverse('userliste') )

###################################################################
# Die Gesamtliste der Teams (TblOrga)
class TeamListView(LoginRequiredMixin, generic.ListView):
	"""Die Gesamtliste der Teams (TblOrga)"""
	model = TblOrga

class TblOrgaCreate(LoginRequiredMixin, CreateView):
	"""Neues Team erstellen"""
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblOrgaUpdate(LoginRequiredMixin, UpdateView):
	"""Team ändern"""
	model = TblOrga
	fields = '__all__'
class TblOrgaDelete(LoginRequiredMixin, DeleteView):
	"""Team löschen"""
	model = TblOrga
	success_url = reverse_lazy('teamliste')

# Paginierung nach Tutorial - Aufteilung langer Seiten in mehrere
def pagination(request, liste, psize=20):
	pagesize = request.GET.get('pagesize')
	if type(pagesize) == type(None) or pagesize == '' or int(pagesize) < 1:
		pagesize = psize  # default, kann man von außen übersteuern
	else:
		pagesize = int(pagesize)
	paginator = Paginator(liste, pagesize)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return (paginator, pages, pagesize)

###################################################################
# Panel geht direkt auf die Gesamt-Datentabelle
@login_required
def panel(request):
	"""
	# Filter-Panel zum Selektieren aus der Gesamttabelle nach allen möglichen Kriterien
	# Beachtet werden die relevanten Foreign Keys
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	(paginator, pages, pagesize) = pagination(request, panel_list)
	context = {
		'paginator': paginator,
		'filter': panel_filter,
		'pages': pages,
		'meineTabelle': panel_list,
		'pagesize': pagesize,
		'gesamtzahl': panel_list.count()
	}
	return render(request, 'rapp/panel_list.html', context)


###################################################################
# Panel_UhR betrachtet den Soll-Zustand über UserHatRolle

@login_required
def panelDownload(request):
	"""
	Exportfunktion für das Filter-Panel zum Selektieren aus der Gesamttabelle (s. panel()).
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	pagesize = request.GET.get('pagesize')
	if pagesize is None or pagesize == "" or int(pagesize) < 1:
		pagesize = 20
	else:
		pagesize = int(pagesize)

	paginator = Paginator(panel_list, 100000)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	context = {
		'paginator': paginator,
		'filter': panel_filter,
		'pages': pages,
		'meineTabelle': panel_list,
		'pagesize': pagesize,
	}
	f = PanelFilter(request.GET, queryset=TblGesamt.objects.all())
	print('Anzahl Elemete in panel_list:', panel_list.count())

	response = HttpResponse(content_type="text/csv")
	response['Content-Distribution'] = 'attachment; filename="gesamt.csv"' # ToDo Hänge Datum an Dateinamen an

	writer = csv.writer(response, delimiter = ',')
	writer.writerow([
		'tf', 'tf_beschreibung',
		'enthalten_in_af',
		'name', 'userid', 'team',
		'name_af_neu', 'name_gf_neu'
	])

	for obj in pages:
		writer.writerow([
			obj.tf, obj.tf_beschreibung,
			obj.enthalten_in_af,
			obj.userid_name.name, obj.userid_name.userid, obj.userid_name.zi_organisation,
			obj.modell.name_af_neu, obj.modell.name_gf_neu
		])

	return response

###################################################################
# Dialogsteuerung für den Import einer neuen IIQ-Datenliste (csv-Datei)
@login_required
def import_csv(request):
	"""
	Importiere neue CSV-Datei mit IIQ-Daten

	Das Verfahren geht über mehrere HTML-Seiten,
	demzufolge befindet sich hier auch die Abbildung als Automat über mehrere Schritte.

	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""

	zeiten = { 'import_start': timezone.now(), } # Hier werden Laufzeiten vermerkt

	def patch_datum(deutsches_datum):
		"""
		# Drehe das deutsche Datumsformat um in das amerikanische und hänge TZ-Info an

		:param deutsches_datum:
		:return: Datum im amerikanischen Format einschließlich Zeitzonen-Information für DE
		"""
		if deutsches_datum == "" or deutsches_datum == None:
			return None
		datum = deutsches_datum.split ('.')
		if len (datum) != 3:
			return deutsches_datum		# Dann passt das Datumsformat nicht
		return  datum[2] + '-' + datum[1] + '-' + datum[0] + ' 00:00+0100'

	def leere_importtabelle():
		"""
		# Löscht alle Einträge aus der Importtabelle sowie der Übertragungstabelle

		:return: Nichts, außer Einträgen in zeiten[]
		"""
		# Löscht alle Einträge aus der Importtabelle sowie der Übertragungstabelle
		zeiten['leere_start'] = timezone.now()
		Tblrechteneuvonimport.objects.all().delete()
		Tblrechteamneu.objects.all().delete()
		zeiten['leere_ende'] = timezone.now()

	def schreibe_zeilen(reader):
		"""
		Für jede Zeile der Eingabedatei soll genau eine Zeile in der Importtabelle erzeugt werden

		:param reader: Der übergebene Reader mit geöffneter CSV-Datei
		:return: void; zeiten[]
		"""
		zeiten['schreibe_start'] = timezone.now()

		request.session['geschafft'] = 0  # Das darf man nicht abkürzen wegen leerer Dateien!
		for line in reader:
			# Sicherheitshalber werden alle eingelesenen Daten auf Maximallänge reduziert.
			# Derzeit gibt es bereits Einträge in 'TF Name' und 'TF Beschreibung',
			# die die Grenzen bei weitem überschreiten.
			neuerRecord = Tblrechteneuvonimport(
				identitaet = 			textwrap.shorten (line['Identität'], width=150, placeholder="..."),
				nachname = 				textwrap.shorten (line['Nachname'], width=150, placeholder="..."),
				vorname = 				textwrap.shorten (line['Vorname'], width=150, placeholder="..."),
				tf_name = 				textwrap.shorten (line['TF Name'], width=100, placeholder="..."),
				tf_beschreibung = 		textwrap.shorten (line['TF Beschreibung'], width=250, placeholder="..."),
				af_anzeigename = 		textwrap.shorten (line['AF Anzeigename'], width=100, placeholder="..."),
				af_beschreibung = 		textwrap.shorten (line['AF Beschreibung'], width=250, placeholder="..."),
				hoechste_kritikalitaet_tf_in_af = textwrap.shorten (line['Höchste Kritikalität TF in AF'],
																	width=150, placeholder="..."),
				tf_eigentuemer_org = 	textwrap.shorten (line['TF Eigentümer Org'], width=150, placeholder="..."),
				tf_applikation = 		textwrap.shorten (line['TF Applikation'], width=250, placeholder="..."),
				tf_kritikalitaet = 		textwrap.shorten (line['TF Kritikalitätskennzeichen'], width=150, placeholder="..."),
				gf_name = 				textwrap.shorten (line['GF Name'], width=150, placeholder="..."),
				gf_beschreibung = 		textwrap.shorten (line['GF Beschreibung'], width=250, placeholder="..."),
				direct_connect = 		textwrap.shorten (line['Direct Connect'], width=150, placeholder="..."),
				af_zugewiesen_an_account_name = textwrap.shorten (line['AF Zugewiesen an Account-Name'],
																  width=150, placeholder="..."),
				af_gueltig_ab = 		patch_datum (line['AF Gültig ab']),
				af_gueltig_bis = 		patch_datum (line['AF Gültig bis']),
				af_zuweisungsdatum = 	patch_datum (line['AF Zuweisungsdatum']),
			)
			neuerRecord.save()
			request.session['geschafft'] = request.session.get('geschafft', 0) + 1 # Zeilenzähler
		zeiten['schreibe_ende'] = timezone.now()
		del request.session['geschafft']
		del request.session['Anzahl Zeilen']

	def hole_datei():
		"""
		Über die HTTP-Verbindung kommt eine Datei, die auf CSV-Inhalte geprüft werden muss

		:return: zeilen_der_Datei, der_Dialekt_der_Datei (CSV, TSV, ...); Dialoect wird durch sniff() ermittelt
		"""
		datei = request.FILES['datei']
		inhalt = datei.read().decode("ISO-8859-1")	# Warum das kein UTF-8 ist, weiß ich auch nicht
		zeilen = inhalt.splitlines()
		request.session['Anzahl Zeilen'] = len(zeilen) - 1	# Merken für Fortschrittsbalken, 1. Zeile ist Header

		dialect = csv.Sniffer().sniff(zeilen[0])
		dialect.escapechar = '\\'
		return (zeilen, dialect)

	def bearbeite_datei(ausgabe):
		"""
		Liest die im Web angegebene Datei ein und versucht, sie in der Übergabetabelle zu hinterlegen.
		ToDo Die Fehlerbehandlung muss verbessert werden

		:param ausgabe: boolean flag, ob die Funktion Textausgaben erzeugen soll (debug)
		:return: Laufzeiten-Summen der Funktionen zum Einlesen und Bearbeiten
		"""
		if ausgabe: print('Organisation =', form.cleaned_data['organisation'])
		zeilen, dialect = hole_datei()
		reader = csv.DictReader(zeilen, dialect=dialect)

		"""
		Wenn das bis hierhin ohne Fehler gelaufen ist, müsste der Rest auch funktionieren.
		Deshalb werden jetzt erst mal die verschiedenen Importtabellen geleert
		"""
		leere_importtabelle()
		schreibe_zeilen(reader)

		zeiten['import_ende'] = timezone.now()
		laufzeiten = { # Laufzeit ist immer gefüllt, bei den beiden anderen kann Unvorhergesehenes passieren
			'Laufzeit':		str(zeiten['import_ende'] - zeiten['import_start']),
		}
		if 'leere_ende' in zeiten and 'leere_start' in zeiten:
			laufzeiten['Leeren'] = str(zeiten['leere_ende'] - zeiten['leere_start'])
		if 'schreibe_ende' in zeiten and 'schreibe_start' in zeiten:
			laufzeiten['Schreiben'] = str(zeiten['schreibe_ende'] - zeiten['schreibe_start'])

		if ausgabe:
			for line in laufzeiten:
				print (line)
		return laufzeiten

	def import_schritt1(orga):
		"""
		# Führt die beiden ersten Stored Procedures vorbereitung() und neueUser() zum Datenimport aus

		:param orga: String der Organisation, für die die Daten eingelesen werden sollen (wichtig für User-ID-Match)
		:return: Statistik: was alles geändert werden soll; Fehlerinformation (False = kein Fehler)
		"""
		fehler = False
		statistik = {}
		with connection.cursor() as cursor:
			try:
				s = 1
				cursor.callproc ("vorbereitung")
				s = 2
				cursor.callproc ("neueUser", [orga, ])
				tmp = cursor.fetchall()
				# print (tmp)
				for line in tmp:
					statistik[line[0]] = line[1]
			except:
				e = sys.exc_info()[0]
				fehler = format("Error: %s" % e)
				if s == 1:
					print ('Fehler in import_schritt1, StoredProc "vorbereitung"', fehler)
				elif s == 2:
					print ('Fehler in import_schritt1, StoredProc "neueUser"', fehler)
				else:
					print('Fehler in import_schritt1, aber wo?', fehler, 's =', s)

			cursor.close()
			return statistik, fehler

	__DUMMY__ = False #or True	# Das 'or True' auskommentieren, wenn die Funktion unten genutzt werden sol
	if request.method == 'POST':
		form = ImportForm(request.POST, request.FILES)
		if form.is_valid():
			if not __DUMMY__:
				orga = request.POST.get('organisation', 'Keine Orga!') # Auf dem Panel wurde die Ziel-Orga übergeben
				request.session['organisation'] = orga	# und merken in der Session für Schritt 3
				laufzeiten = bearbeite_datei(False)
				statistik, fehler = import_schritt1(orga)
				request.session['import_statistik'] = statistik
				request.session['import_laufzeiten'] = laufzeiten
				request.session['fehler1'] = fehler
			return redirect('import2')
	else:
		form = ImportForm(initial={'organisation': 'AI-BA'}, auto_id=False)

	context = {
		'form': form,
		'version': version,
	}
	return render (request, 'rapp/import.html', context)


@login_required
def import2(request):
	"""
	Der zweite Schritt zeigt zunächst die statistischen Ergebnisse von Schritt 1, dann die neuen User
	Soewie die zu löschenden User.
	Beim Bestätigen des Schrittes werden die neuen User der UserIDundName-Tabelle hinzugefügt
	und die zu löschenden markiert sowie deren Rechte historisiert
	(warum eigentlich, die können doch bei der Reinkaranation wieder verwendet werden?).

	:param request: Der POST- oder GET-Request vom Browser
	:return: HTML-Output
	"""
	def hole_alles(db):
		"""
		Lesen aller Werte aus einer übergebenen Datenbank
		Das wird benötigt für Datenbanken, die nicht als Django-Modell hinterlegt sind (bspw. temp.-Tabellen)

		:param db: Welche Datenbank soll gelesen werden?
		:return: Die gelesenen Zeilen; Fehler-Information (False = kein Fehler)
		"""
		fehler = False
		retval = [['Nix geladen']]
		with connection.cursor() as cursor:
			try:
				sql = "SELECT * FROM {}".format(db)
				cursor.execute (sql)
				retval = cursor.fetchall()
			except:
				e = sys.exc_info()[0]
				fehler = format("Error: %s" % e)

			cursor.close()
			return retval, fehler

	def hole_neueUser():
		"""
		Lies alle Einträge von DB qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a (temporäre Tabelle beim Import)

		:return: Die Einträge
		"""
		return hole_alles('qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a')

	def hole_geloeschteUser():
		"""
		Lies alle Einträge von DB qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a (temporäre Tabelle beim Import)

		:return: Die Einträge
		"""
		return hole_alles('qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a')

	def import_schritt2():
		"""
		Führt die Stored Procedure behandleUser() zum Aktualisieren der UserIDundName-Tabelle aus
		Als Seiteneffekt werden die Tabellen qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
		und qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a gefüllt, die weiter unten in die Session übernommen werden.

		:return: Fehler-Information (False = kein Fehler)
		"""
		fehler = False
		with connection.cursor() as cursor:
			try:
				cursor.callproc ("behandleUser") # diese SProc benötigt die Orga nicht als Parameter
			except:
				e = sys.exc_info()[0]
				fehler = format("Error: %s" % e)
				print('Fehler in import_schritt2, StoredProc behandleUser', fehler)

			cursor.close()
			return fehler

	if request.method == 'POST':
		form = forms.Form(request.POST) # Kein Eintrag in forms.py erfordelrich, da keine Modell-Anbindung oder Felder
		if form.is_valid():
			fehler = import_schritt2()
			request.session['fehler2'] = fehler
			return redirect('import2_quittung')
		else:
			print ('Form war nicht valide')
	else:
		form = forms.Form()

	"""
	Der Context wird beim ersten Aufruf (dem ersten Anzeigen) des Templates geüllt.
	Bei eventuellen weiteren GET-Lieferunngen wird der Context erneut gesetzt.
	"""
	# ToDo: Nochmal überlegen, was in die Session gehört und was nicht. Session-Vars direkt im Template behandeln!

	context = {
		'form': form,
		'fehler': request.session.get('fehler1', None),
		'statistik': request.session.get('import_statistik', 'Keine Statistik vorhanden'),
		'laufzeiten': request.session.get('import_laufzeiten', 'Keine Laufzeiten vorhanden'),
		'version': version,
	}
	request.session['neueUser'] = hole_neueUser()[0]  # Nur die Daten, ohne den Returncode der Funktion
	request.session['geloeschteUser'] = hole_geloeschteUser()[0]  # Nur die Daten, ohne den Returncode der Funktion
	return render(request, 'rapp/import2.html', context)


@login_required
def import2_quittung(request):
	"""
	Nun erfolgt eine Ausgabe, ob das Verändern der User-Tabelle geklappt hat.
	Es wird ein Link angeboten auf eine geeignete Seite, um die User-Tabelle manuell anzupassen.
	Buttons werden angeboten, um den nächsten Schritt anzustoßen oder das Ganze abzubrechen.

	:param request: GET- oder POST-Request
	:return: HTML-Output
	"""
	def import_schritt3(orga, dopp):
		# Führt die letzte definitiv erforderliche Stored Procedures behandle_Rechte() aus.
		# Optional kann dann noch das Löschen doppelt angelegeter Rechte erfolgen (loescheDoppelteRechte)
		fehler = False
		with connection.cursor() as cursor:
			try:
				retval = cursor.callproc ("behandleRechte", [orga, ])
				if dopp:
					retval += cursor.callproc ("loescheDoppelteRechte", [False, ]) # False = Nicht nur lesen
				retval += cursor.callproc ("ueberschreibeModelle")

			except:
				e1 = sys.exc_info()[0]
				e2 = sys.exc_info()[1]
				fehler = format("Error: %s %s" % e1, e2)
				print ('Fehler in import_schritt2, StoredProc behandleUser oder loescheDoppelteRechte oder ueberschreibeModelle', fehler)

			cursor.close()
			return fehler

	if request.method == 'POST':
		form = ImportForm_schritt3(request.POST)
		if form.is_valid():
			orga = request.session.get('organisation', 'keine-Orga')
			dopp = request.POST.get('doppelte_suchen', False)

			fehler = import_schritt3(orga, dopp)

			request.session['fehler3'] = fehler
			ergebnis = TblGesamt.objects.filter(geloescht = False,
										 userid_name__zi_organisation = orga,
										 userid_name__geloescht = False).count()
			request.session['ergebnis'] = ergebnis
			return redirect('import3_quittung')
		else:
			print ('Form war nicht valide')
	else:
		form = ImportForm_schritt3(initial={'doppelte_suchen': False})

	context = {
		'form': form,
		'fehler': request.session.get('fehler2', None),
		'version': version,
	}
	return render(request, 'rapp/import2_quittung.html', context)


@login_required
def import3_quittung(request):
	"""
	Der dritte Schritt des Imports zeigt nur noch das Ergebnis der Stored Procs an

	:param request: GET- oder POST-Request
	:return: HTML-Output
	"""
	context = {
		#'form': form,
		#'fehler': request.session.get('fehler3', None),
		'version': version,
	}
	return render(request, 'rapp/import3_quittung.html', context)

@login_required
def import_status(request):
	"""
	Das wird vielleicht mal die ReST-Datenlieferung für einen Fortschrittsbalken.
	Dazu muss aber das Einlesen der Daten parallel zu anderen Funktionen laufen können,
	das ist noch nicht wirklich innerhalb dieser Funktionen gegeben
	(kein nebenläufiges Update der Session-Information parallel zum Einlesen der Datei).

	:param request: GET- oder POST-Request
	:return: HTML-Output
	"""
	zeilen = request.session.get ('Anzahl Zeilen', 1)
	aktuell = request.session.get ('geschafft', 0)
	proz = int(aktuell) * 100 // int(zeilen)
	print (zeilen, aktuell, proz)
	return render (request, 'rapp/import_status.html', {'proz': proz, 'version': version, })
