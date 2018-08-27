# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Create your views here.

from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.paginator import Paginator
from .filters import PanelFilter

# Zum Einlesen der csv
# import tablib
# from tablib import Dataset
# from import_export import resources
# from .resources import MyCSVImporterModel
from rapp.models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform, Tblrechteneuvonimport

###################################################################
# RApp - erforderliche Sichten und Reports

# ToDo: Alle User und ihre Rollen für eine Selektion

# ToDo: Alle User und ihre Rollen sowie die daran hängenden AF für eine Selektion (nur zur Ansicht und Veränderung, kein PDF)
# Kombinieren UserundIhreRollen mit RollenundIhre AF


# ToDo: Alle Rollen sowie die daran hängenden AF für eine Selektion (gruppiert für PDF)

# ToDo: Alle TF / GF / AF / Rollen für selektierte User
# ToDo: - Evtl. gibt es das schon beim jetzigen Filterpanel

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

from django.http import HttpResponse

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
# Die Gesamtliste der Rechte ungefiltert
class GesamtListView(generic.ListView):
	model = TblGesamt
	paginate_by = 50

# Die Detailsicht eines einzelnen Rechts
class GesamtDetailView(generic.DetailView):
	model = TblGesamt


###################################################################
# Die Gesamtliste der User ungefiltert
class UserIDundNameListView(generic.ListView):
	model = TblUserIDundName
	paginate_by = 50

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class TblUserIDundNameCreate(CreateView):
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblUserIDundNameUpdate(UpdateView):
	model = TblUserIDundName
	fields = '__all__'

class TblUserIDundNameDelete(DeleteView):
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
	model = TblOrga

class TblOrgaCreate(CreateView):
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblOrgaUpdate(UpdateView):
	model = TblOrga
	fields = '__all__'

class TblOrgaDelete(DeleteView):
	model = TblOrga
	success_url = reverse_lazy('teamliste')


###################################################################
# Die Ab hier kommen die Views für das Panel

"""
###################################################################
# Nur zum Zeigen, wie das mit den Panels gehen könnte....

def search(request):
	user_list = User.objects.all()
	user_filter = UserFilter(request.GET, queryset=user_list)
	return render(request, 'rapp/user_list.html', {'filter': user_filter})
"""

###################################################################
# Panel geht direkt auf die Gesamt-Datentabelle

def panel(request):
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

