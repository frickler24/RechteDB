from __future__ import unicode_literals
# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.utils import timezone
from django import forms

from .filters import PanelFilter, UseridFilter
from .views import version
from .forms import ShowUhRForm, CreateUhRForm, ImportForm, ImportForm_schritt3
from .models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform, TblUserhatrolle, \
					Tblrechteneuvonimport, Tblrechteamneu
from .xhtml2 import render_to_pdf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


###################################################################
# Zuordnungen der Rollen zu den Usern (TblUserHatRolle ==> UhR)
class UhRCreate(LoginRequiredMixin, CreateView):
	"""
	Erzeugt einen neue Rolle für einen User.
	Die Rolle kann eine bestehende oder eine neu definierte Rolle sein.
	"""
	model = TblUserhatrolle
	template_name = 'rapp/uhr_form.html'
	form_class = CreateUhRForm

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		context['userid'] = self.kwargs['userid']
		user_entry = TblUserIDundName.objects.filter(userid__istartswith=self.kwargs['userid'])[0]
		context['username'] = user_entry
		return context

	def get_form_kwargs(self):
		kwargs = super(UhRCreate, self).get_form_kwargs()
		kwargs['userid'] = self.kwargs['userid']
		return kwargs

	# Im Erfolgsfall soll die vorherige Selektion im Panel "User und Rollen" wieder aktualisiert gezeigt werden.
	# Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
	def get_success_url(self):
		usernr = self.request.GET.get('user', 0) # Sicherheitshalber - falls mal kein User angegeben ist

		urlparams = "%s?"
		for k in self.request.GET.keys():
			if (k != 'user' and self.request.GET[k] != ''):
				urlparams += "&" + k + "=" + self.request.GET[k]
		url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
		# print (url)
		return url
class UhRDelete(LoginRequiredMixin, DeleteView):
	"""Löscht die Zuordnung einer Rollen zu einem User."""
	model = TblUserhatrolle
	template_name = 'rapp/uhr_confirm_delete.html'

	# Im Erfolgsfall soll die vorherige Selektion im Panel "User und RolleN" wieder aktualisiert gezeigt werden.
	# Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
	def get_success_url(self):
		usernr = self.request.GET.get('user', 0) # Sicherheitshalber - falls mal kein User angegeben ist

		urlparams = "%s?"
		for k in self.request.GET.keys():
			if (k != 'user' and self.request.GET[k] != ''):
				urlparams += "&" + k + "=" + self.request.GET[k]
		url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
		return url
class UhRUpdate(LoginRequiredMixin, UpdateView):
	"""Ändert die Zuordnung von Rollen zu einem User."""
	# ToDo: Hierfür gibt es noch keine Buttons.
	model = TblUserhatrolle
	fields = '__all__'

	# Im Erfolgsfall soll die vorherige Selektion im Panel "User und RolleN" wieder aktualisiert gezeigt werden.
	# Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
	def get_success_url(self):
		usernr = self.request.GET.get('user', 0) # Sicherheitshalber - falls mal kein User angegeben ist

		urlparams = "%s?"
		for k in self.request.GET.keys():
			if (k != 'user' and self.request.GET[k] != ''):
				urlparams += "&" + k + "=" + self.request.GET[k]
		url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
		# print (url)
		return url


def UhR_erzeuge_listen(request):
	"""
	Finde alle relevanten Informationen zur aktuellen Selektion:

	Ausgangspunkt ist TblUseridUndName.
	Hierfür gibt es einen Filter, der per GET abgefragt wird.
	Geliefert werden nur die XV-Nummern zu den Namen (diese muss es je Namen zwingend geben)

	Die dort gefundene Treffermenge wird angereichert um die relevanten Daten aus TblUserHatRolle.
	Hier werden allerdings alle UserIDen zurückgeliefert je Name.
	Von dort aus gibt eine ForeignKey-Verbindung zu TblRollen.

	Problematisch ist noch die Verbindung zwischen TblRollen und TblRollaHatAf,
	Weil hier der Foreign Key Definition in TblRolleHatAf liegt.
	Das kann aber aufgelöst werden,
	sobald ein konkreter User betrachtet wird und nicht mehr eine Menge an Usern.

	:param request: GET oder POST Request vom Browser
	:param pk: optional: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
	:return: name_liste, panel_liste, panel_filter
	"""
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

	return (namen_liste, panel_liste, panel_filter)

def Uhr_hole_daten(panel_liste, id):
	"""
	Selektiere alle Userids und alle Namen in TblUserHatRolle, die auch in der Selektion vorkommen

	Die Liste der disjunkten UserIDs wird später in der Anzeige benötigt (Welche UserID gehören zu einem Namen).
	Hintergrund ist die Festlegung, dass die Rollen am UserNAMEN un dnicht an der UserID hängen.
	Dennoch gibt es Rollen, die nur zu bestimmten Userid-Typen (also bspw. nur für XV-Nummer) sinnvoll
	und gültig sind.

	Die af_menge wird benutzt zur Anzeige, welche der rollenbezogenen AFen bereits im IST vorliegt

	"""
	usernamen = set()	# Die Namen aller User,  die in der Selektion erfasst werden
	userids = set()		# Die UserIDs aller User,  die in der Selektion erfasst werden
	afmenge = set()		# Die Menge aller AFs aller mit ID spezifizierten User (für Berechtigungskonzept)
	selektierte_userids = set()	# Die Liste der UserIDs, die an Identität ID hängen
	afmenge_je_userID = {}	# Menge mit USERID-spezifischen AF-Listen

	for row in panel_liste:
		usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
		userids.add(row.userid)

	if (id != 0):  # Dann wurde der ReST-Parameter 'id' mitgegeben

		userHatRolle_liste = TblUserhatrolle.objects.filter(userid__id=id).order_by('rollenname')
		selektierter_name = TblUserIDundName.objects.get(id = id).name

		# Wahrscheinlich werden verschiedene Panels auf die Haupt-UserID referenzieren (die XV-Nummer)
		selektierte_haupt_userid = TblUserIDundName.objects.get(id = id).userid

		# Hole alle UserIDs, die zu dem ausgesuchten User passen.
		# Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
		# Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen
		number_of_userids = TblUserIDundName.objects\
			.filter(name = selektierter_name)\
			.filter(geloescht = False)\
			.count()
		for num in range(number_of_userids):
			selektierte_userids.add (TblUserIDundName.objects
									 .filter(name = selektierter_name)
									 .order_by('-userid') \
									 .filter(geloescht=False)[num].userid)

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
		afliste = TblUserIDundName.objects.get(id=id).tblgesamt_set.all()  # Das QuerySet
		for e in afliste:
			afmenge.add(e.enthalten_in_af)  # Filtern der AFen aus der Treffermenge

		# Erzeuge zunächst die Hashes für die UserIDs. daran werden nachher die Listen der Rechte gehängt
		for uid in selektierte_userids:
			afmenge_je_userID[uid] = set()

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit den konkreten UserIDs verknüpft sind.
		for uid in selektierte_userids:
			tmp_afliste = TblUserIDundName.objects.get(userid = uid).tblgesamt_set.all()  # Das QuerySet
			for e in tmp_afliste:
				afmenge_je_userID[uid].add(e.enthalten_in_af)  # Element and die UserID-spezifische Liste hängen
	else:
		userHatRolle_liste = []
		selektierter_name = -1
		selektierte_haupt_userid = 'keine_userID'

	return (userHatRolle_liste, selektierter_name, userids, usernamen,
			selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID)

def pagination(request, namen_liste):
	"""Paginierung nach Tutorial"""
	pagesize = request.GET.get('pagesize')
	if type(pagesize) == type(None) or pagesize == '' or int(pagesize) < 1:
		pagesize = 100  # Eigentlich sollte hier nie gepaged werden, dient nur dem Schutz vor Fehlabfragen
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

	return (paginator, pages, pagesize)

@login_required
def panel_UhR(request, id = 0):
	"""
	Finde alle relevanten Informationen zur aktuellen Selektion:

	:param request: GET oder POST Request vom Browser
	:param pk: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
	:return: Gerendertes HTML
	"""

	(namen_liste, panel_liste, panel_filter) = UhR_erzeuge_listen(request)

	if request.method == 'POST':
		form = ShowUhRForm(request.POST)
		print ('Irgendwas ist im panel_UhR über POST angekommen')

		if form.is_valid():
			return redirect('home')  # TODO: redirect ordentlich machen oder POST-Teil entfernen
	else:
		(userHatRolle_liste, selektierter_name, userids, usernamen,
		 selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID) \
			= Uhr_hole_daten(panel_liste, id)
		(paginator, pages, pagesize) = pagination(request, namen_liste)

	form = ShowUhRForm(request.GET)
	context = {
		'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
		'filter': panel_filter,
		'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
		'userHatRolle_liste': userHatRolle_liste,
		'id': id,
		'form': form,
		'selektierter_name': selektierter_name,
		'selektierte_userid': selektierte_haupt_userid,
		'selektierte_userids': selektierte_userids,
		'afmenge_je_userID': afmenge_je_userID,
		'version': version,
	}
	return render(request, 'rapp/panel_UhR.html', context)

# Funktionenzum Erstellen des Berechtigungskonzepts
def UhR_verdichte_daten(panel_liste):
	"""
	Ausgehend von den Userids der Selektion zeige
	  für jeden User (nur die XV-User zeigen auf Rollen, deshalb nehmen wir nur diese)
	    alle Rollen mit allen Details
	      einschließlich aller darin befindlicher AFen mit ihren formalen Zuweiseungen (Soll-Bild)
	        verdichtet auf Mengenbasis
			  (keine Doppelnennungen von Rollen,
			  aber ggfs. Mehrfachnennungen von AFen,
			  wenn sie in Rollen mehrfach enthalten sind)

	Ergebnis ist Liste von

	"""
	usernamen = set()
	userids = set()
	rollenMenge = set()

	for row in panel_liste:
		if row.userid[:2].lower() == "xv":
			usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
			userids.add(row.userid)
			userHatRollen = TblUserhatrolle.objects.filter(userid__userid=row.userid).order_by('rollenname')
			for e in userHatRollen:
				rollenMenge.add(e.rollenname)

	def order(a): return a.rollenname.lower() 	# Liefert das kleingeschriebene Element, nach dem sortiert werden soll
	return (sorted(list(rollenMenge), key=order), userids, usernamen)

@login_required
def panel_UhR_konzept_pdf(request):
	return UhR_konzept(request, False)

def panel_UhR_konzept_ansicht(request):
	return UhR_konzept(request, True)

def	UhR_konzept(request, ansicht):
	"""
	Erzege das Berechtigungskonzept für eine Menge an selektierten Identitäten.

	:param request: GET Request vom Browser
	:return: Gerendertes HTML
	"""

	# Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
	(namen_liste, panel_liste, panel_filter) = UhR_erzeuge_listen(request)

	if request.method == 'GET':
		(rollenMenge, userids, usernamen) = UhR_verdichte_daten(panel_liste)
	else:
		(rollenMenge, userids, usernamen) = (set(), set(), set())

	(paginator, pages, pagesize) = pagination(request, namen_liste)

	if request.GET.get('display') == '1':
			print('rollenMenge')
			print(rollenMenge)

			print('userids')
			for a in userids:
				print(a)

			print('usernamen')
			for a in usernamen:
				print(a)

	context = {
		'paginator': paginator, 'pages': pages, 'pagesize': 20,
		'filter': panel_filter,
		'rollenMenge': rollenMenge,
		'version': version,
	}
	if (ansicht):
		return render(request, 'rapp/panel_UhR_konzept.html', context)

	pdf = render_to_pdf('rapp/panel_UhR_konzept_pdf.html', context)
	if pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Berechtigungskonzept_%s.pdf" % ("erstmalnurtest_123")
		content = "inline; filename='%s'" % (filename)
		download = request.GET.get("download")
		if download:
			content = "attachment; filename='%s'" % (filename)
		response['Content-Disposition'] = content
		return response
	return HttpResponse("Fehlerhafte PDF-Generierung")

