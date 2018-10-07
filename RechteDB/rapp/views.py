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
from .filters import PanelFilter, UseridFilter

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django import forms

from .forms import ShowUhRForm, ImportForm, ImportForm_schritt3

# Zum Einlesen der csv
import csv, textwrap

from .models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform, TblUserhatrolle, \
	Tblrechteneuvonimport, Tblrechteamneu

# An dieser stelle stehen diverse Tools zum Aufsetzen der Datenbank mit SPs
from .stored_procedures import *

###################################################################
# RApp - erforderliche Sichten und Reports

# ToDo: Alle Rollen sowie die daran hängenden AF für eine Selektion (gruppiert für PDF)

# ToDo: Alle TF / GF / AF / Rollen für selektierte User - Evtl. gibt es das schon beim jetzigen Filterpanel

# ToDo: Abgleich vorhandener Rechte selektierter User mit Zertifizierungsliste

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

# ToDo: Suche-Panel: Die Links bei den beiden Lösch-Buttons rechts sind defekt
# ToDo: Links auf die change- create- und delete-Seiten ausprobieren. Sind eigene Seiten im Frontend besser?
# ToDo: Filter-Panel mit excel Export versorgen
# ToDo: Kompakte Liste für Rolle und AF mit Filtermöglichkeit und PDF Generierung

# ToDo: Die gesamten Modellnamen können mal überarbeitet werden (kein TBL am Anfang etc.)

# ToDo: in UserHatRollen ist in der Anzeige die "aktiv"-Anzeige für eine AF noch nicht auf die einzelnen UserIDs der Identität bezogen, sondern gilt "generell"
# ToDo: Die tables alternierend einfärben
# ToDo: Prüfen, warum so viele Plattvorm_id in der Gesamttabelle 0 sind
# ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller userids benötigt wird, sonst in SP löschen nach Nutzung
# ToDO: Längenbegrenzungen checken in Modell für UserHatRolle
# ToDo Mechismus für die progress-bar geht überhaupt noch nicht (kein Update, kein Löschen usw.)

# Der Direkteinsteig für die gesamte Anwendung
def home(request):
	# Zeige ein paar Statistik-Infos über die RechteDB.
	# Das stellt sicher, dass die Anbidnung an die Datenbank funzt
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
class GesamtListView(generic.ListView):
	# Die Gesamtliste der Rechte ungefiltert
	model = TblGesamt
	paginate_by = 50
class GesamtDetailView(generic.DetailView):
	# Die Detailsicht eines einzelnen Rechts
	model = TblGesamt

###################################################################
# Rechte-User (Gemeint sind nicht die Anwender der RechteDB!)
class UserIDundNameListView(generic.ListView):
	# Die Gesamtliste der User ungefiltert
	model = TblUserIDundName
	paginate_by = 50
class TblUserIDundNameCreate(CreateView):
	# Erstellen eines neuen Users
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblUserIDundNameUpdate(UpdateView):
	# Ändern eines Users
	model = TblUserIDundName
	fields = '__all__'
class TblUserIDundNameDelete(DeleteView):
	# Löschen eines Users
	model = TblUserIDundName
	success_url = reverse_lazy('userliste')
def userToggleGeloescht(request, pk):
	# View function zum Togglen des Gelöscht-Flags in der DB für eine konkrete Instanz.
	# Dieser Aufruf wird nicht in zwei Schritten als GET / POST-Kombination durchgeführt.
	# sondern ausschließlich als GET.
	user_inst = get_object_or_404(TblUserIDundName, pk = pk)

	user_inst.geloescht = not user_inst.geloescht
	user_inst.save()

	# redirect to a new URL:
	return HttpResponseRedirect(reverse('userliste') )


###################################################################
# Die Gesamtliste der Teams (TblOrga)
class TeamListView(generic.ListView):
	# Die Gesamtliste der Teams (TblOrga)
	model = TblOrga
class TblOrgaCreate(CreateView):
	# Neues Team erstellen
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblOrgaUpdate(UpdateView):
	# Team ändern
	model = TblOrga
	fields = '__all__'
class TblOrgaDelete(DeleteView):
	# Team löschen
	model = TblOrga
	success_url = reverse_lazy('teamliste')


###################################################################
# Zuordnungen der Rollen zu den Usern (TblUserHatRolle ==> UhR)
class UhRCreate(CreateView):
	# Erzeugt einen neue Rolle für einen User.
	# Die Rolle kann eine bestehende oder eine neu definierte Rolle sein.
	model = TblUserhatrolle
	template_name = 'rapp/uhr_form.html'
	fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung']
	context_object_name = 'unser_user'
class UhRUpdate(UpdateView):
	# Ändert die Zuordnung von Rollen zu einem User.
	model = TblUserhatrolle
	fields = '__all__'
class UhRDelete(DeleteView):
	# Löscht die Zuordnung einer Rollen zu einem User.
	model = TblUserhatrolle
	template_name = 'rapp/uhr_confirm_delete.html'
	success_url = reverse_lazy('user_rolle_af') # ToDo Die Rücksprungadresse bei Success parametrisieren (wie?)


###################################################################
# Panel geht direkt auf die Gesamt-Datentabelle

def panel(request):
	# Filter-Panel zum Selektieren aus der Gesamttabelle nach allen möglichen Kriterien
	# Beachtet werden die relevanten Foreign Keys
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	pagesize = request.GET.get('pagesize')

	if type(pagesize) == type(None) or int(pagesize) < 1:
		pagesize = 20
	else:
		pagesize = int(pagesize)

	paginator = Paginator(panel_list, pagesize)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	args = {'paginator': paginator, 'filter': panel_filter, 'pages': pages, 'meineTabelle': panel_list, 'pagesize': pagesize}
	return render(request, 'rapp/panel_list.html', args)


###################################################################
# Panel_UhR betrachtet den Soll-Zustand über UserHatRolle

def panel_UhR(request, id = 0):
	# Finde alle relevanten Informationen zur aktuellen Selektion:
	#
	# Ausgangspunkt ist TblUseridUndName.
	# Hierfür gibt es einen Filter, der per GET abgefragt wird.
	# Geliefert werden nur die XV-Nummern zu den Namen (diese muss es je Namen zwingend geben)
	#
	# Die dort gefundene Treffermenge wird angereichert um die relevanten Daten aus TblUserHatRolle.
	# Hier werden allerdings alle UserIDen zurückgeliefert je Name.
	# Von dort aus gibt eine ForeignKey-Verbindung zu TblRollen.
	#
	# Problematisch ist noch die Verbindung zwischen TblRollen und TblRollaHatAf,
	# Weil hier der Foreign Key Definition in TblRolleHatAf liegt.
	# Das kann aber aufgelöst werden,
	# sobald ein konkreter User betrachtet wird und nicht mehr eine Menge an Usern.

	panel_liste = TblUserIDundName.objects.filter(geloescht=False).order_by('name')
	panel_filter = UseridFilter(request.GET, queryset=panel_liste)
	namen_liste = panel_filter.qs.filter(userid__istartswith="xv")
	panel_liste = panel_filter.qs.select_related("orga")

	"""
	# Ein paar Testzugriffe über das komplette Modell
	#   Hier ist die korrekte Hierarchie abgebildet von UserID bis AF:
    #   TblUserIDundName ethält Userid
    #       TblUserHatRolle hat FK 'userid' auf TblUserIDundName
    #       -> tbluserhatrolle_set.all auf eine aktuelle UserID-row liefert die Menge der relevanten Rollen
    #           Rolle hat ForeignKey 'rollenname' auf TblRolle und erhält damit die nicht-User-spezifischen Rollen-Parameter
    #               TblRolleHatAF hat ebenfalls einen ForeignKey 'rollennname' auf TblRollen
    #               -> rollenname.tblrollehataf_set.all liefert für eine konkrete Rolle die Liste der zugehörigen AF-Detailinformationen
	#
	#		TblGesamt hat FK 'userid_name' auf TblUserIDundName
	#		-> .tblgesamt_set.filter(geloescht = False) liefert die akiven Arbeitsplatzfunktionen
	#

	user = TblUserIDundName.objects.filter(userid = 'XV13254')[0]
	print ('1:', user)
	foo = user.tbluserhatrolle_set.all()
	print ('2:', foo)

	for x in foo:
		print ('3:', x, ',', x.rollenname, ',', x.rollenname.system)
		foo2 = x.rollenname.tblrollehataf_set.all()
		for y in foo2:
			print ('4:', y, ', AF=', y.af, ', Muss:', y.mussfeld, ', Einsatz:', y.einsatz)
	af_aktiv = user.tblgesamt_set.filter(geloescht = False)
	af_geloescht = user.tblgesamt_set.filter(geloescht = True)
	print ("5: aktive AF-Liste:", af_aktiv, "geloescht-Liste:", af_geloescht)
	for x in af_aktiv:
		print ('5a:', x.enthalten_in_af, x.tf, x.tf_beschreibung, sep = ', ')
	print
	for x in af_geloescht:
		print ('5b:', x.enthalten_in_af, x.tf, x.tf_beschreibung, sep = ', ')
	print
	af_liste = TblUserIDundName.objects.get(id=id).enthalten_in_af
	print ('6:', af_liste)
	"""

	if request.method == 'POST':
		form = ShowUhRForm(request.POST)
		print ('Irgendwas ist angekommen')	# ToDo Hä?

		if form.is_valid():
			return redirect('home')  # TODO: redirect ordentlich machen

	else:
		# Selektiere alle Userids und alle Namen in TblUserHatRolle, die auch in der Selektion vorkommen
		# Hier könnte man mal einen reverse lookup einbauen von TblUserUndName zu TblUserHatRolle
		#
		# Die Liste der disjunkten UserIDs wird später in der Anzeige benötigt (Welche UserID gehören zu einem Namen).
		# Hintergrund ist die Festlegung, dass die Rollen am UserNAMEN un dnicht an der UserID hängen.
		# Dennoch gibt es Rollen, die nur zu bestimmten Userid-Typen (also bspw. nur für XV-Nummer) sinnvoll
		# und gültig sind.
		#
		# Die af_menge wird benutzt zur Anzeige, welcche der rollenbezogenen AFen bereits im IST vorliegt
		#
		usernamen = set()
		userids = set()
		for row in panel_liste:
			usernamen.add (row.name)	# Ist Menge, also keine Doppeleinträge möglich
			userids.add (row.userid)

		if (id != 0):	# Dann wurde der ReST-Parameter 'id' mitgegeben

			userHatRolle_liste = TblUserhatrolle.objects.filter(userid__id=id).order_by('rollenname')
			selektierter_name = TblUserIDundName.objects.get(id=id).name
			selektierte_userid = TblUserIDundName.objects.get(id=id).userid

			# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
			afliste = TblUserIDundName.objects.get(id=id).tblgesamt_set.all()	# Das QuerySet
			afmenge = set()
			for e in afliste:
				afmenge.add(e.enthalten_in_af)	# Filtern der AFen aus der Treffermenge
		else:
			userHatRolle_liste = []
			selektierter_name = -1
			selektierte_userid = 'keine_userID'
			afmenge = set()

		# Paginierung nach Tutorial
		pagesize = request.GET.get('pagesize')
		if type(pagesize) == type(None) or pagesize == '' or int(pagesize) < 1:
			pagesize = 100	# Eigentlich sollte hier nie gepaged werden, dient nur dem Schutz vor Fehlabfragen
		else:
			pagesize = int(pagesize)
		paginator = Paginator(namen_liste, pagesize)
		page = request.GET.get('page', 1)
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
			pages = paginator.page(1)
		except EmptyPage:
			pages = paginator.page(paginator.num_pages)

	form = ShowUhRForm(request.GET)
	args = {
		'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
		'filter': panel_filter,
		'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
		'userHatRolle_liste': userHatRolle_liste,
		'id': id,
		'form': form,
		'selektierter_name': selektierter_name,
		'selektierte_userid': selektierte_userid,
	}

	return render(request, 'rapp/panel_UhR.html', args)


###################################################################
# Dialogsteuerung für den Import einer neuen IIQ-Datenliste (csv-Datei)

def import_csv(request):
	# Importiere neue CSV-Datei mit IIQ-Daten
	zeiten = { 'import_start': timezone.now(), } # Hier werden Laufzeiten vermerkt

	def patch_datum(deutsches_datum):
		# Drehe das deutsche Datumsformat um in das amerikanische und hänge TZ-Info an
		if deutsches_datum == "" or deutsches_datum == None:
			return None
		datum = deutsches_datum.split ('.')
		if len (datum) != 3:
			return deutsches_datum		# Dann passt das Datumsformat nicht
		return  datum[2] + '-' + datum[1] + '-' + datum[0] + ' 00:00+0100'

	def leere_importtabelle():
		# Löscht alle Einträge aus der Importtabelle sowie der Übertragungstabelle
		zeiten['leere_start'] = timezone.now()
		Tblrechteneuvonimport.objects.all().delete()
		Tblrechteamneu.objects.all().delete()
		zeiten['leere_ende'] = timezone.now()

	def schreibe_zeilen(reader):
		# Für jede Zeile der Eingabedatei soll genau eine Zeile in der Importtabelle erzeugt werden
		zeiten['schreibe_start'] = timezone.now()

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
				tf_kritikalitaet = 		textwrap.shorten (line['TF Kritikalität'], width=150, placeholder="..."),
				gf_name = 				textwrap.shorten (line['GF Name'], width=150, placeholder="..."),
				gf_beschreibung = 		textwrap.shorten (line['GF Beschreibung'], width=250, placeholder="..."),
				direct_connect = 		textwrap.shorten (line['Direct Connect'], width=150, placeholder="..."),
				af_zugewiesen_an_account_name = textwrap.shorten (line['AF zugewiesen an Account-Name'],
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
		# Über die HTTP-Verbindung kommt eine Datei, die auf CSV-Inhalte geprüft werden muss
		datei = request.FILES['datei']
		inhalt = datei.read().decode("ISO-8859-1")	# Warum das kein UTF-8 ist, weiß ich auch nicht
		zeilen = inhalt.splitlines()
		request.session['Anzahl Zeilen'] = len(zeilen) - 1	# Merken für Fortschrittsbalken, 1. Zeile ist Header

		dialect = csv.Sniffer().sniff(zeilen[0])
		dialect.escapechar = '\\'
		return (zeilen, dialect)

	def bearbeite_datei(ausgabe):
		# Liest die im Web angegebene Datei ein und versucht, sie in der Übergabetabelle zu hinterlegen.
		# ToDo Die Fehlerbehandlung muss verbessert werden
		if ausgabe: print('Organisation =', form.cleaned_data['organisation'])
		zeilen, dialect = hole_datei()
		reader = csv.DictReader(zeilen, dialect=dialect)

		# Wenn das bis hierhin ohne Fehler gelaufen ist, müsste der Rest auch funktionieren.
		# Deshalb werden jetzt erst mal die verschiedenen Importtabellen geleert
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
		# Führt die beiden ersten Stored Procedures vorbereitung() und neueUser() zum Datenimport aus
		fehler = False
		statistik = {}
		with connection.cursor() as cursor:
			try:
				s = 1
				cursor.callproc ("vorbereitung")
				s = 2
				cursor.callproc ("neueUser", [orga, ])
				tmp = cursor.fetchall()
				print (tmp)
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
			print ('Form war nicht valide')
	else:
		form = ImportForm(initial={'organisation': 'AI-BA'}, auto_id=False)

	context = {
		'form': form,
	}
	return render (request, 'rapp/import.html', context)


def import2(request):
	# Der zweite Schritt zeigt zunächst die statistischen Ergebnisse von Schritt 1, dann die neuen User
	# Soewie die zu löschenden User.
	# Beim Bestätigen des Schrittes werden die neuen User der UserIDundName-Tabelle hinzugefügt
	# und die zu löschenden markiert sowie deren Rechte historisiert
	# (warum eigentlich, die können doch bei der Reinkaranation wieder verwendet werden?).

	def hole_alles(db):
		# Lesen aller Werte aus eienr übergebenen Datenbank
		# Das wird benötigt für Datenbanken, die nicht als Django-Modell hinterlegt sind (bspw. temp.-Tabellen)
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
		return hole_alles('qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a')

	def hole_geloeschteUser():
		return hole_alles('qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a')

	def import_schritt2():
		# Führt die Stored Procedure behandleUser() zum Aktualisieren der UserIDundName-Tabelle aus
		# Als Seiteneffekt werden die Tabellen qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
		# und qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a gefüllt, die weiter unten in die Session übernommen werden.
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

	# Der Context wird beim ersten Aufruf (dem ersten Anzeigen) des Templates geüllt.
	# Bei eventuellen weiteren GET-Lieferunngen wird der Context erneut gesetzt.
	# ToDO:_ Nopchmal überlegen, was in die Session gehört und was nicht. Session-Vars direkt im Template behandeln!
	context = {
		'form': form,
		'fehler': request.session.get('fehler1', None),
		'statistik': request.session.get('import_statistik', 'Keine Statistik vorhanden'),
		'laufzeiten': request.session.get('import_laufzeiten', 'Keine Laufzeiten vorhanden'),
	}
	request.session['neueUser'] = hole_neueUser()[0]  # Nur die Daten, ohne den Returncode der Funktion
	request.session['geloeschteUser'] = hole_geloeschteUser()[0]  # Nur die Daten, ohne den Returncode der Funktion
	return render(request, 'rapp/import2.html', context)


def import2_quittung(request):
	# Nun erfolgt eine Ausgabe, ob das Verändern der User-Tabelle geklappt hat.
	# Es wird ein Link angeboten auf eine geeignete Seite, um die User-Tabelle manuell anzupassen.
	# Buttons werden angeboten, um den nächsten Schritt anzustoßen oder das Ganze abzubrechen.

	def import_schritt3(orga, dopp):
		# Führt die letzte definitiv erforderliche Stored Procedures behandle_Rechte() aus.
		# Optional kann dann noch das Löschen doppelt angelegeter Rechte erfolgen (loescheDoppelteRechte)
		fehler = False
		with connection.cursor() as cursor:
			try:
				retval = cursor.callproc ("behandleRechte", [orga, ])
				print (retval)
				if dopp:
					retval += cursor.callproc ("loescheDoppelteRechte", [False, ]) # False = Nicht nur lesen

			except:
				e = sys.exc_info()[0]
				fehler = format("Error: %s" % e)
				print ('Fehler in import_schritt2, StoredProc behandleUser oder loescheDoppelteRechte', fehler)

			cursor.close()
			return fehler

	if request.method == 'POST':
		form = ImportForm_schritt3(request.POST)
		if form.is_valid():
			orga = request.session.get('organisation', 'keine-Orga')
			dopp = request.POST.get('doppelte_suchen', False)

			print (orga, dopp)
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
	}
	return render(request, 'rapp/import2_quittung.html', context)


def import3_quittung(request):
	context = {
		#'form': form,
		#'fehler': request.session.get('fehler3', None),
	}
	return render(request, 'rapp/import3_quittung.html', context)

def import_status(request):
	zeilen = request.session.get ('Anzahl Zeilen', 1)
	aktuell = request.session.get ('geschafft', 0)
	proz = int(aktuell) * 100 // int(zeilen)
	print (zeilen, aktuell, proz)
	return render (request, 'rapp/import_status.html', {'proz': proz})
