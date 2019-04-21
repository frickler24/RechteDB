# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Zum Einlesen der Versionsnummer
import os, re, subprocess, sys
from math import *

def hole_namen(zeile):
	return ("Hans Meier", "xv98765")

def latex_header():
	s = """\\documentclass[a4paper,landscape,12pt]{letter}
	\\usepackage[paper=a4paper,height=18cm,left=25mm,right=20mm,width=22cm]{geometry}
	\\usepackage[ngerman]{babel} % Deutsche Einstellungen Syntaxcheck
	\\usepackage[utf8]{inputenc} % Eingabe-Encoding
	\\usepackage[T1]{fontenc}	% Ausgaben mit vollen Fonts
	\\usepackage{csquotes}
	%\\usepackage{pdflscape}
	\\usepackage{longtable}
	
	\\parindent0cm
	\\pagestyle{headings}
	
	\\title{\\textbf{Betreff:} Rechtezuordnung als Direct Connect}
	\\date{\\today}
	
	\\address{G\\_BA-Berechtigungs\\-rezertifizierungsgedöns \\\\ZI-AI-BA (McGyver)}
	
	\\begin{document}
	% If you want headings on subsequent pages,
	% remove the ``%'' on the next line:
	% \\pagestyle{headings}
	
	"""
	return s + "\n"

def latex_identitaeten():
	# Hole per SQL die Namen und UserIDs
	return (("name", "userid"))

def latex_adresse(userid):
	s = "\\begin{letter}{"
	s += ("{}@ruv.de \\hfill \\break".format(userid))
	s += "}"
	return s + "\n"


def latex_anrede(name):
	s = """\\begin{normalsize}
	\\opening{\\textbf{Betreff:} Rechtezuordnung als \\emph{Direct Connect}}
	\\begin{normalsize} \\hfill
	\\end{normalsize}

	\\begin{normalsize}
		Guten Tag, 
	"""
	s += "{}".format(name)
	s += """ \\hfill \\break
	\\end{normalsize}
	\\end{normalsize}
	"""
	return s + "\n"

def latex_einleitungstext():
	s = """\\begin{normalsize}
	Ihnen sind derzeit eines oder mehrere Rechte als sogenannte \\emph{Direct Connects} zugeordnet.
	
	Diese Zuordnung wird zum 01.06.2019 im Rahmen der aktuellen Rezertifizierung der Berechtigungen gelöscht.
	
	Falls Sie die unten aufgeführte Berechtigung nicht für Ihre Aufgaben benötigen, brauchen Sie nichts weiter zu veranlassen.
	
	Anderenfalls wenden Sie sich bitte rechtzeitig an Ihre IT-Betreuer und lassen Sie sich die bestgeeignete der unten angegebenen Arbeitsplatzfunktionen zuordnen:
	\\end{normalsize}
	"""
	return s + "\n"

def hole_daten(name):
	return ()

def hole_tf_liste(datenzeilen):
	return 	"TF1\\\\ TF2\\\\ TF3\\\\\n"

def latex_tf_liste(datenzeilen):
	s = """\\begin{normalsize}
	Nachfolgend die Liste der Ihnen direkt zugeordneten technischen Funktionen (TF):

	\\begin{longtable}{l}
		Entitlement (TF) \\\\ \\hline
		\\endfirsthead
		\\multicolumn{1}{@{}l}{\\ldots Fortsetzung}\\\\\\hline
		Entitlement (TF) \\\\ \\hline
		\\endhead % all the lines above this will be repeated on every page
		\\multicolumn{1}{r@{}}{Fortsetzung \\ldots}\\\\
		\\endfoot
		\\hline
		\\endlastfoot
	"""
	s += hole_tf_liste(datenzeilen)
	s += """	\\end{longtable}
	\\end{normalsize}
	"""
	return s + "\n"

def latex_tabellenkopf():
	s = """\\begin{tiny}
	\\begin{longtable}{|p{20mm}|p{15mm}|p{25mm}|p{10mm}|p{30mm}|p{40mm}|p{40mm}|}
		\\hline
		Entitlement & Applikation & Identität & Account-Name & AF & Neue Beschreibung der AF & Alte Beschreibung der AF\\\\ \\hline
		\\endfirsthead
		\\multicolumn{7}{@{}l}{\\ldots Fortsetzung}\\\\\\hline
		Entitlement (TF) \\\\ \\hline
		\\endhead % all the lines above this will be repeated on every page
		\\hline \\multicolumn{7}{r@{}}{Fortsetzung \\ldots}\\\\
		\\endfoot
		\\hline
		\\endlastfoot
	"""
	return s + "\n"

def hole_af_varianten(datenzeilen):
	s = ""
	for i in range (100):
		s += "AF-Variante {} & 2 & 3 & 4 & 5 & 6 & 7\\\\\n".format(i)
	s += """\\hline
	\\end{longtable}
	\\end{tiny}
	"""
	return s + "\n"

def latex_abspann():
	s = """\\begin{normalsize}
	Bei Fragen zu technischen Hintergründen können Sie oder Ihre IT-Betreuer sich an den Gruppenbriefkasten wenden.
	\\end{normalsize}
	
	\\begin{normalsize}
		Beste Grüße\\\\Lutz Eichler
	\\end{normalsize}
	
	
	%enclosure listing
	%\\encl{}
	
	\\end{letter}
	\\end{document}
	"""
	return s + "\n"


@login_required
def serienbrief(request):
	"""
	Exportfunktion für das Filter-Panel zum Selektieren aus der "User und Rollen"-Tabelle).
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
	"""
	if request.method != 'GET':
		return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_matrix_csv")

	text = latex_header()
	zeilen = latex_identitaeten()

	for zeile in zeilen:
		brief = text
		(name, userid) = hole_namen(zeile)
		brief += latex_adresse(userid)
		brief += latex_anrede(name)
		brief += latex_einleitungstext()

		datenzeilen = hole_daten(name)
		brief += latex_tf_liste(datenzeilen)
		brief += latex_tabellenkopf()
		brief += hole_af_varianten(datenzeilen)
		brief += latex_abspann()

	print(brief)

	response = HttpResponse(content_type="text/text")
	response['Content-Distribution'] = 'attachment; filename="Serienbrief.tex"'

	writer = Writer(response)
	writer.writerow(brief)

	return response
