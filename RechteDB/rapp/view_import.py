# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect

from django.utils import timezone
from django import forms

from django.contrib.auth.decorators import login_required

# Zum Einlesen der csv
import csv, datetime, textwrap, sys
from math import *

from .forms import ImportForm, ImportForm_schritt3
from .models import TblGesamt, Tblrechteneuvonimport, Tblrechteamneu, Letzter_import

# An dieser stelle stehen diverse Tools zum Aufsetzen der Datenbank mit SPs
from .stored_procedures import connection
from .views import version
import time
def neuer_import(request):
	"""
	:return: Fehler-Flag (True: In Retval steht ein Fehler-beschreibendes HTML, False: ein Objekt wurde erzeugt)
	:return: retval: Fehlerbeschreibung oder neues Datenobjekt in Modell-Klasse Letzter_import
	"""
	fehler = False
	# Zunächst versuche zu ermitteln, ob gerade ein anderer Import läuft:
	try:
		# Das nachfolgende Statement kann schon mal schiefgehen, z.B. wenn die DB noch leer ist.
		letzter_import_im_modell = Letzter_import.objects.latest('id')
		if letzter_import_im_modell.end is None:
			# Dann läuft gerade ein anderer Import, sonst wäre das end-Feld gesetzt
			# oder der letzte Import ist abgebrochen
			request.session['parallel_start'] = str(letzter_import_im_modell.start)
			request.session['parallel_user'] = letzter_import_im_modell.user
			fehlermeldung = render(request, 'rapp/import_parallel.html')
			return (True, fehlermeldung)  # True signalisiert "Fehler"
	except:
		# print('Fehler bei Erkennung der Ende-Markierung. Kann aber ganz normal eine leere DB sein.')
		pass

	# Legt ein neues Datenobjekt zum Markieren des Import-Status an, speichert aber erst weiter unten
	letzter_import = Letzter_import(start = timezone.now(), schritt = 1)
	return (False, letzter_import)	# False signalisiert "Alles OK, weitermachen"

def speichere_schritt(import_datum):
	import_datum.save()

def naechster_schritt(request, schrittnummer):
	"""
	:param request: Der HTTP-Request mit den relevanten Session-Informationen
	:param schrittnummmer: Welcher Schritt soll als nächstes ausgeführt werden?
	:return: None: Alles OK; Sonst ein Fehler-HTML zur Anzeige.
	"""
	erwarteter_schritt = -1
	try:
		# Das nachfolgende Statement darf nun nicht mehr schiefgehen
		letzter_import_im_modell = Letzter_import.objects.latest('id')
		if letzter_import_im_modell.end is None:
			# In diesem Fall ist das gut, weil ja unser Import läuft.
			erwarteter_schritt = letzter_import_im_modell.schritt + 1
			if schrittnummer == erwarteter_schritt:
				letzter_import_im_modell.schritt = schrittnummer
				letzter_import_im_modell.save()
				return False  # Kein Fehler gefunden, Nummer wurde aktualisiert
	except:
		pass

	# Die beiden Session-Varaiblen werden im Template für die Fehlermeldung erwartet
	request.session['erwarteter_schritt'] = erwarteter_schritt
	request.session['geforderter_schritt'] = schrittnummer
	return render(request, 'rapp/import_schrittfehler.html')

def letzter_schritt():
	"""
	:param request: HTTP_Request für mögliche Fehlermeldung / Session-Daten
	:return: --
	"""
	try:
		# Das nachfolgende Statement darf nun nicht mehr schiefgehen
		letzter_import_im_modell = Letzter_import.objects.latest('id')
		if letzter_import_im_modell.end is None:
			# In diesem Fall ist das gut, weil ja unser Import läuft.
			letzter_import_im_modell.schritt = letzter_import_im_modell.schritt + 1
			letzter_import_im_modell.end = timezone.now()
			letzter_import_im_modell.save()  # Damit ist der Datensatz für diesen Schritt endgültig fertig.
	except:
		pass

	return


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

	# Zunächst versuche zu ermitteln, ob gerade ein anderer Import läuft:
	# Legt ein neues Datenobjekt zum Markieren des Import-Status an, speichert aber erst weiter unten
	(fehler, import_datum) = neuer_import(request)
	if (fehler):
		return import_datum

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
		import_datum.max = request.session['Anzahl Zeilen']
		del request.session['Anzahl Zeilen']

		import_datum.aktuell = 0
		speichere_schritt(import_datum)	# Jetzt wird das Objekt erst in der DB wirklich angelegt

		current_user = request.user
		import_datum.user = current_user.username

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
			import_datum.aktuell += 1
			if import_datum.aktuell % 42 == 0:
				speichere_schritt(import_datum)

		zeiten['schreibe_ende'] = timezone.now()
		speichere_schritt(import_datum)	# Damit ist der Datensatz für diesen Schritt endgültig fertig.

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
				fehler = 'Error in import_schritt1(): {}'.format(e)
				if s == 1:
					print ('Fehler in import_schritt1, StoredProc "vorbereitung"', fehler)
				elif s == 2:
					print ('Fehler in import_schritt1, StoredProc "neueUser"', fehler)
				else:
					print('Fehler in import_schritt1, aber wo?', fehler, 's =', s)

			cursor.close()
			return statistik, fehler

	if request.method == 'POST':
		form = ImportForm(request.POST, request.FILES)
		if form.is_valid():
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
				fehler = 'Error in hole_alles(): {}'.format(e)

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
				fehler = 'Error in import_schritt2(): {}'.format(e)
				print('Fehler in import_schritt2, StoredProc behandleUser', fehler)

			cursor.close()
			return fehler

	if request.method == 'POST':
		retval = naechster_schritt(request, 2)  # Jetzt wird der nächste Schritt aufgesetzt
		if retval:
			return retval  # Dann ist ein Schrittfehler aufgetreten und retval enthält die Fehlermeldung

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
				fehler = 'Error in import_schritt3(): {} {}'.format(e1, e2)
				print ('Fehler in import_schritt2, StoredProc behandleUser oder loescheDoppelteRechte oder ueberschreibeModelle', fehler)

			cursor.close()
			return fehler

	if request.method == 'POST':
		retval = naechster_schritt(request, 3)  # Jetzt wird der nächste Schritt aufgesetzt
		if retval:
			return retval  # Dann ist ein Schrittfehler aufgetreten und retval enthält die Fehlermeldung

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
	retval = naechster_schritt(request, 4)  # Jetzt wird der nächste Schritt aufgesetzt
	if retval:
		return retval  # Dann ist ein Schrittfehler aufgetreten und retval enthält die Fehlermeldung
	letzter_schritt()

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
	:param request: GET- oder POST-Request
	:return: HTML-Output
	"""
	try:
		letzter_import_im_modell = Letzter_import.objects.latest('id') # Die aktuelle Zeile
		if letzter_import_im_modell.end is None:
			# In diesem Fall ist das gut, weil ja unser Import läuft.
			context = {
				'version': version,
				'aktuell': letzter_import_im_modell.aktuell,
				'zeilen': letzter_import_im_modell.max,
				'proz': int(letzter_import_im_modell.aktuell) * 100 // int(letzter_import_im_modell.max),
			}
		else:
			context = {
				'version': version,
				'aktuell': -2 ,
				'zeilen': -2 ,
				'proz': -2 ,
			}
	except:
		context = {
			'version': version,
			'aktuell': -1,
			'zeilen': -1,
			'proz': -1,
		}

	return render(request, 'rapp/import_status.html', context)


@login_required
def import_reset(request):
	print('Harter Reset angefordert in import_reset()')
	try:
		letzter_import_im_modell = Letzter_import.objects.latest('id')
		letzter_import_im_modell.end = timezone.now()
		current_user = request.user
		letzter_import_im_modell.user = current_user.username
		letzter_import_im_modell.user = '{} / {}'.format(current_user.username, 'explizit zurückgesetzt')
		letzter_import_im_modell.save()
	except:
		print('Harter Reset hat Problem in import_reset():', letzter_import_im_modell.id, ':',
			  letzter_import_im_modell.start, letzter_import_im_modell.end,
			  letzter_import_im_modell.max, letzter_import_im_modell.aktuell, letzter_import_im_modell.user)

	return redirect('import')
