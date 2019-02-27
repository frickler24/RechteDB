from __future__ import unicode_literals
# Create your views here.


from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect

from django.views.generic.edit import CreateView, UpdateView, DeleteView
import csv

from .filters import RollenFilter, UseridFilter
from .views import version, pagination
from .forms import ShowUhRForm, CreateUhRForm, ImportForm, ImportForm_schritt3
from .models import TblUserIDundName, TblGesamt, TblRollehataf, TblUserhatrolle
from .xhtml2 import render_to_pdf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .templatetags.gethash import finde

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
	weil hier der Foreign Key Definition in TblRolleHatAf liegt.
	Das kann aber aufgelöst werden,
	sobald ein konkreter User betrachtet wird und nicht mehr eine Menge an Usern.

	:param request: GET oder POST Request vom Browser
	:param pk: optional: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
	:return: name_liste, panel_liste, panel_filter
	"""
	panel_liste = TblUserIDundName.objects.filter(geloescht=False).order_by('name')
	panel_filter = UseridFilter(request.GET, queryset=panel_liste)

	namen_liste = panel_filter.qs.filter(userid__istartswith="xv")
	panel_liste = panel_filter.qs.filter(userid__istartswith="xv").select_related("orga")

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

def UhR_erzeuge_listen_ohne_rollen(request):
	"""
	Liefert zusätzlich zu den Daten aus UhR_erzeuge_listen noch eine leere Rollenliste,
	damit das Suchfeld angezeigt wird
	:param request:
	:return: namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter
	"""

	# Hole erst mal eine leere Rollenliste ud dazu passenden Filter
	rollen_liste = TblUserhatrolle.objects.none()
	rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

	# Und nun die eigentlich wichtigen Daten holen
	(namen_liste, panel_liste, panel_filter) = UhR_erzeuge_listen(request)
	return (namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter)

def UhR_erzeuge_listen_mit_rollen(request):
	"""
	Liefert zusätzlich zu den Daten aus UhR_erzeuge_listen noch die dazu gehörenden Rollen
	:param request:
	:return: namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter
	"""

	# Hole erst mal die Menge an Rollen, die namentlich passen
	suchstring = request.GET.get('rollenname', 'nix')
	print('Suchstring:', suchstring)
	rollen_liste = TblUserhatrolle.objects.filter(rollenname__rollenname__icontains = suchstring).order_by('rollenname')
	rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)
	print ('Anzahl Rollen:', len(rollen_liste))

	userids = set ()
	for x in rollen_liste:
		userids.add(x.userid.userid)

	(_, panel_liste, panel_filter) = UhR_erzeuge_listen(request)
	namen_liste = (panel_filter.qs.filter(userid__in = userids))
	print('Gefilterte Namenliste:', namen_liste)

	return (namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter, userids)

def finde_userids_zum_namen(selektierter_name):
	"""
	Hole alle UserIDs, die zu dem ausgesuchten User passen.
	Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
	Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen

	:param selektierter_name: Zu welcehm Namen sollen die UserIDs gesucht werden?
	:return: Liste der UserIDs (als Strings)
	"""
	selektierte_userids = set()	# Die Menge der UserIDs, die an Identität ID hängen

	number_of_userids = TblUserIDundName.objects \
		.filter(name=selektierter_name) \
		.filter(geloescht=False) \
		.count()
	for num in range(number_of_userids):
		selektierte_userids.add(TblUserIDundName.objects
								.filter(name=selektierter_name)
								.order_by('-userid') \
								.filter(geloescht=False)[num].userid)
	return selektierte_userids

# Selektiere die erforderlichen User- und Berefchtigungsdaten
def UhR_hole_daten(panel_liste, id):
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
	afmenge_je_userID = {}	# Menge mit UserID-spezifischen AF-Listen

	for row in panel_liste:
		usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
		userids.add(row.userid)

	if (id != 0):  # Dann wurde der ReST-Parameter 'id' mitgegeben

		userHatRolle_liste = TblUserhatrolle.objects.filter(userid__id=id).order_by('rollenname')
		selektierter_name = TblUserIDundName.objects.get(id = id).name

		# Wahrscheinlich werden verschiedene Panels auf die Haupt-UserID referenzieren (die XV-Nummer)
		selektierte_haupt_userid = TblUserIDundName.objects.get(id = id).userid

		# Hole alle UserIDs, die zu dem ausgesuchten User passen.
		selektierte_userids = finde_userids_zum_namen(selektierter_name)

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
		afliste = TblUserIDundName.objects.get(id=id).tblgesamt_set.all()  # Das QuerySet
		for e in afliste:
			afmenge.add(e.enthalten_in_af)  # Filtern der AFen aus der Treffermenge

		# Erzeuge zunächst die Hashes für die UserIDs.
		# Daran werden nachher die Listen der Rechte gehängt.
		for uid in selektierte_userids:
			afmenge_je_userID[uid] = set()

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit den konkreten UserIDs verknüpft sind.
		for uid in selektierte_userids:
			tmp_afliste = TblUserIDundName.objects.get(userid = uid).tblgesamt_set.all()  # Das QuerySet
			for e in tmp_afliste:
				afmenge_je_userID[uid].add(e.enthalten_in_af)  # Element an die UserID-spezifische Liste hängen
	else:
		userHatRolle_liste = []
		selektierter_name = -1
		selektierte_haupt_userid = 'keine_userID'

	return (userHatRolle_liste, selektierter_name, userids, usernamen,
			selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID)

def finde_rollen(userid, af, rolle):
	"""
	Liefert die Liste der Rollen, in denen eine bestimmte AF vorkommt.
	:param name: Die gerade betrachtete UserID des users
	:param af: Name der gesuchten Arbeitsplatzfunktion AF
	:param rolle: Name der gesuchten Rolle; Nur dazu passende AFen zurückliefern
	:return: vorhanden = Liste der Rollen, in denen die AF vorkommt und die dem Namen zugeordnet sind
	:return: optional = Liste der Rollen, in denen die AF vorkommt und die dem User nicht zugeordnet sind
	"""
	# Hole erst mal die Menge an Rollen, die namentlich zu der AF passen
	print('Gesuchte UserID:', userid, '; Suche nach AF:', af)
	if rolle is None:
		rollen_liste = TblRollehataf.objects.filter(af__af_name = af).order_by('rollenname')
	else:
		rollen_liste = TblRollehataf.objects\
			.filter(rollenname = rolle)\
			.filter(af__af_name = af)\
			.order_by('rollenname')
	print ('Rollen_liste: ', rollen_liste)

	# Wenn die Kombination Rollenname und Userid nicht passt, liefere leere Listen zurück
	rolle_passt = TblUserhatrolle.objects\
		.filter(userid__userid = userid)\
		.filter(rollenname__rollenname = rolle)
	if rolle_passt == 0:
		return ([], [])

	# Ansonsten suche alle Rollen, in denen die AF enthalten ist und prüfe, ob die UserID diese AF besitzt
	vorhanden = set()
	optional = set()
	gefunden = TblGesamt.objects.filter(enthalten_in_af = af)\
		.filter(geloescht = False)\
		.filter(userid_name__userid = userid) \
		.filter(userid_name__geloescht = False)

	print ('Anzahl gefundene AF-Einträge (mehrere TFen) für die Userid:', len(gefunden))
	if len(gefunden) > 0:
		vorhanden.add(af)
	else:
		optional.add(af)

	print('Vorhanden:', list(vorhanden))
	print('Optional :', list(optional))
	return (list(vorhanden), list(optional))

def UhR_hole_rollen_daten(namen_liste, gesuchte_rolle):
	"""
	Finde alle UserIDs, die über die angegebene Rolle verfügen.
	Wenn gesuchte_rolle is None, dann finde alle Rollen.
	:param namen_liste: Zu welchen Namen soll die Liste erstellt werden?
	:param gesuchte_rolle: s.o.
	:return: ToDo: Weiß noch nicht genau
	"""
	# Erzeuge die Liste der UserID, die mit den übergebenen Namen zusammenhängen
	# Dann erzeuge die Liste der AFen, die mit den UserIDs verbunden sind
	# - Notiere für jede der AFen, welche Rollen Grund für diese AF derzeit zugewiesen sind (aus UserHatRolle)
	# - Notiere, welche weiteren Rollen, die derzeit nicht zugewiesen sind, für diese AF in Frage kämen
	# Gib alles in einer fetten Datenstruktur zurück.

	gesamt_liste = {}

	for name in namen_liste:
		print('Starte mit Namen:', name.name)
		userids = finde_userids_zum_namen(name.name)
		print('UserIDs:', userids)

		for userid in userids:
			af_liste = TblGesamt.objects.filter(userid_name_id__userid = userid).filter(geloescht = False).distinct()
			print (len(af_liste))

			af_menge = {}
			for af in af_liste:
				if af.enthalten_in_af not in af_menge:
					(vorhandene_rollen, optionale_rollen) = finde_rollen(userid, af.enthalten_in_af, gesuchte_rolle)
					af_menge[af.enthalten_in_af] = (vorhandene_rollen, optionale_rollen)

			gesamt_liste[userid] = (name, af_liste, af_menge)

	print ('Gesamt_liste', gesamt_liste)

	assert 0, 'schluss'
	#return (userHatRolle_liste, selektierter_name, userids, usernamen, selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID)

# Funktionen zum Erstellen des Berechtigungskonzepts
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

# Die beidnen nachfolgenden Funktionen dienen nur dem Aufruf der eigentlichen Konzept-Funktion
@login_required
def panel_UhR_konzept_pdf(request):
	return UhR_konzept(request, False)

@login_required
def panel_UhR_konzept(request):
	return UhR_konzept(request, True)

class UhR(object):
	def factory(typ):
		if typ == 'einzel':
			return EinzelUhr()
		if typ == 'rolle':
			return RollenListenUhr()
		if typ == 'af':
			return AFListenUhr()
		assert 0, "Falsche Factory-Typ in Uhr: " + typ
	factory = staticmethod(factory)

class EinzelUhr(UhR):
	def behandle(self, request, id):
		"""
		Finde alle relevanten Informationen zur aktuellen Selektion
		Das ist die Factory-Klasse für die Betrachtung einzelner User und deren spezifischer Rollen

		:param request: GET oder POST Request vom Browser
		:param id: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen; 0 -> kein User gewählt
		:return: Gerendertes HTML
		"""
		(namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter) = UhR_erzeuge_listen_ohne_rollen(request)
		(userHatRolle_liste, selektierter_name, userids, usernamen,
		 selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID) \
			= UhR_hole_daten(panel_liste, id)
		(paginator, pages, pagesize) = pagination(request, namen_liste, 10000)

		form = ShowUhRForm(request.GET)
		context = {
			'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
			'filter': panel_filter,
			'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
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

class RollenListenUhr(UhR):
	def behandle(self, request, _):
		"""
		Finde alle relevanten Informationen zur aktuellen Selektion
		Das ist die Factory-Klasse für die Betrachtung aller User mit spezifischen Rollen- oder AF-Namen

		:param request: GET oder POST Request vom Browser
		:param id: wird hier nicht verwendet, deshalb "_"
		:return: Gerendertes HTML
		"""
		(namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter, userids) = UhR_erzeuge_listen_mit_rollen(request)
		print('Namenliste in RollenListenUhR:', namen_liste)

		(userHatRolle_liste, selektierter_name, userids, usernamen, selektierte_haupt_userid, selektierte_userids,
		afmenge, afmenge_je_userID) = UhR_hole_rollen_daten(namen_liste, request.GET.get('rollenname', None))

		#(paginator, pages, pagesize) = pagination(request, afmenge_je_userID, 100)

		form = ShowUhRForm(request.GET)
		context = {
			#'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
			'filter': panel_filter,
			'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
			'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
			'userHatRolle_liste': userHatRolle_liste,
			'id': id,
			'form': form,
			'selektierte_userids': selektierte_userids,
			'afmenge_je_userID': afmenge_je_userID,
			'version': version,
		}
		return render(request, 'rapp/panel_UhR_rolle.html', context)

class AFListenUhr(UhR):
	def behandle(self, request, id):
		return ''

# Zeige das Selektionspanel
@login_required
def panel_UhR(request, id = 0):
	"""
	Finde die richtige Anzeige und evaluiere sie über das factory-Pattern

	:param request: GET oder POST Request vom Browser
	:param pk: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
	:return: Gerendertes HTML
	"""

	assert request.method != 'POST', 'Irgendwas ist im panel_UhR über POST angekommen'
	assert request.method == 'GET', 'Irgendwas ist im panel_UhR nicht über GET angekommen: ' + request.method

	if request.GET.get('rollenname', None) != None and request.GET.get('rollenname', None) != "":
		name = 'rolle'
	elif request.GET.get('afname', None) != None and request.GET.get('afname', None) != "":
		name = 'af'
	else:
		name = 'einzel'

	print (name)
	obj = UhR.factory(name)
	return obj.behandle(request, id)

# Erzeuge das Berechtiogungskonzept für Anzeige und PDF
def	UhR_konzept(request, ansicht):
	"""
	Erzeuge das Berechtigungskonzept für eine Menge an selektierten Identitäten.

	:param request: GET Request vom Browser
	:param ansicht: Flag, ob die Daten als HTML zur Ansicht oder als PDF zum Download geliefert werden sollen
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
		'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
		'filter': panel_filter,
		'rollenMenge': rollenMenge,
		'version': version,
	}
	if (ansicht):
		return render(request, 'rapp/panel_UhR_konzept.html', context)

	pdf = render_to_pdf('rapp/panel_UhR_konzept_pdf.html', context)
	if pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Berechtigungskonzept_%s.pdf" % ("hierMussNochEinVernünftigerNameHin")
		content = "inline; filename='%s'" % (filename)
		download = request.GET.get("download")
		if download:
			content = "attachment; filename='%s'" % (filename)
		response['Content-Disposition'] = content
		return response
	return HttpResponse("Fehlerhafte PDF-Generierung in UhR_konzept")

# Funktionen zum Erstellen des Funktionsmatrix
def UhR_erzeuge_matrixdaten(panel_liste):
	"""
	Überschriften-Block:
		Erste Spaltenüberschrift ist "Name" als String, darunter werden die Usernamen liegen, daneben:
		Ausgehend von den Userids der Selektion zeige
			die Liste der Rollen alle nebeneinander als Spaltenüberschriften
	Zeileninhalte:
		Für jeden User (nur die XV-User zeigen auf Rollen, deshalb nehmen wir nur diese)
			zeige den Usernamen sowie in jeder zu dem User passenden Rolle die Art der Verwendung (S/V/A)
				in Kurz- oder Langversion, je nach Flag

	Zunächst benötigen wir für alle userIDs (sind nur die XV-Nummern) aus dem Panel alle Rollen

	"""
	usernamen = set()	# Die Namen aller User,  die in der Selektion erfasst werden
	rollenmenge = set()		# Die Menge aller AFs aller spezifizierten User (aus Auswahl-Panel)
	rollen_je_username = {} # Die Rollen, die zum Namen gehören

	for row in panel_liste:
		usernamen.add(row.name)

		# Erzeuge zunächst die Hashes für die UserIDs. Daran werden nachher die Listen der Rechte gehängt.
		rollen_je_username[row.name] = set()

		# Hole die Liste der Rollen für den User, die XV-UserID steht im Panel
		rollen = TblUserhatrolle.objects.filter(userid = row.userid).all()

		# Merke die Rollen je Usernamen (also global für alle UserIDs der Identität)
		# sowie die Menge aller gefundenen Rollennamen
		# Achtung: rolle ist nur eine für den User spezifische Linknummer auf das Rollenobjekt.
		for rolle in rollen:
			info = (rolle.rollenname, rolle.schwerpunkt_vertretung)
			rollen_je_username[row.name].add(info)
			rollenmenge.add(rolle.rollenname)

	def order(a): return a.rollenname.lower() 	# Liefert das kleingeschriebene Element, nach dem sortiert werden soll
	return (sorted(usernamen), sorted(list(rollenmenge), key=order), rollen_je_username)

@login_required
def panel_UhR_matrix(request):
	"""
	Erzeuge eine Verantwortungsmatrix für eine Menge an selektierten Identitäten.

	:param request: GET Request vom Browser
	:param ansicht: Flag, ob die Daten als HTML zur Ansicht oder als PDF zum Download geliefert werden sollen
	:return: Gerendertes HTML
	"""

	# Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
	(namen_liste, panel_liste, panel_filter) = UhR_erzeuge_listen(request)

	if request.method == 'GET':
		(usernamen, rollenmenge, rollen_je_username) = UhR_erzeuge_matrixdaten(panel_liste)
	else:
		(usernamen, rollenmenge, rollen_je_username) = (set(), set(), set())

	(paginator, pages, pagesize) = pagination(request, namen_liste)

	if request.GET.get('display') == '1':
			print('usernamen')
			print(usernamen)

			print('rollenmenge')
			for a in rollenmenge:
				print(a)

			print('rollen_je_username')
			for a in rollen_je_username:
				print(a, rollen_je_username[a])

	context = {
		'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
		'filter': panel_filter,
		'usernamen': usernamen,
		'rollenmenge': rollenmenge,
		'rollen_je_username': rollen_je_username,
		'version': version,
	}
	return render(request, 'rapp/panel_UhR_matrix.html', context)

@login_required
def panel_UhR_matrix_csv(request, flag = False):
	"""
	Exportfunktion für das Filter-Panel zum Selektieren aus der "User und Rollen"-Tabelle).
	:param request: GET oder POST Request vom Browser
	:param flag: False oder nicht gegeben -> liefere ausführliche Text, 'kommpakt' -> liefere nur Anfangsbuchstaben
	:return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
	"""
	if request.method != 'GET':
		return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_matrix_csv")

	(namen_liste, panel_liste, panel_filter) = UhR_erzeuge_listen(request)
	(usernamen, rollenmenge, rollen_je_username) = UhR_erzeuge_matrixdaten(panel_liste)

	response = HttpResponse(content_type="text/csv")
	response['Content-Distribution'] = 'attachment; filename="matrix.csv"' # ToDo Hänge Datum an Dateinamen an

	headline = ['Name']
	for r in rollenmenge:
		headline += [r.rollenname]

	writer = csv.writer(response, delimiter = ',', quotechar = "'")
	writer.writerow(headline)

	for user in usernamen:
		line = [user]
		for rolle in rollenmenge:
			if flag:
				wert = list(finde(rollen_je_username[user], rolle))
				if len(wert) > 0:
					line += [wert[0]]
				else:
					line += ['']
			else:
				line += [finde(rollen_je_username[user], rolle)]
		writer.writerow(line)

	return response
