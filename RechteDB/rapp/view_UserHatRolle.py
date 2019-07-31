from __future__ import unicode_literals
# Create your views here.


from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.utils.encoding import smart_str
import csv

from .filters import RollenFilter, UseridFilter
from .views import version, pagination
from .forms import ShowUhRForm, CreateUhRForm, ImportForm, ImportForm_schritt3
from .models import TblUserIDundName, TblGesamt, TblRollehataf, TblUserhatrolle, TblOrga
from .xhtml2 import render_to_pdf
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin

from .templatetags.gethash import finde
from django.utils import timezone

###################################################################
# Zuordnungen der Rollen zu den Usern (TblUserHatRolle ==> UhR)
class UhRCreate(CreateView):
	"""
	Erzeugt einen neue Rolle für einen User.
	Sowohl User als auch Rolle müssen bereits existieren.
	"""
	model = TblUserhatrolle
	template_name = 'rapp/uhr_form.html'
	# Entweder form-Angabe oder Field-Liste
	form_class = CreateUhRForm
	#fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]
	"""
	initial = {
		'userid': 'xv881P7'.upper(),
		# 'rollenname': 'AI-BA Leitung',
		'rollenname': 'Bereitstellung Host',
		'schwerpunkt_vertretung': 'Vertretung',
	}
	print (initial)
	"""


	def get_form_kwargs(self):
		"""
		Definiere die benötigten benannten Parameter
		:return: kwargs mit den Inhalten der Oberklasse und den benötigten Parametern
		"""
		kwargs = super(UhRCreate, self).get_form_kwargs()
		kwargs['rollenname'] = ""
		kwargs['schwerpunkt_vertretung'] = ""
		kwargs['userid'] = self.kwargs['userid']

		if 'rollenname' in self.kwargs:
			kwargs['rollenname'] = self.kwargs['rollenname']
		if 'schwerpunkt_vertretung' in self.kwargs:
			kwargs['schwerpunkt_vertretung'] = self.kwargs['schwerpunkt_vertretung']
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
		print (url)
		return url
class UhRDelete(DeleteView):
	"""Löscht die Zuordnung einer Rollen zu einem User."""
	model = TblUserhatrolle
	template_name = 'rapp/uhr_confirm_delete.html'

	# Im Erfolgsfall soll die vorherige Selektion im Panel "User und RolleN" wieder aktualisiert gezeigt werden.
	# Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
	def get_success_url(self):
		usernr = self.request.GET.get('user', "0") # Sicherheitshalber - falls mal kein User angegeben ist

		urlparams = "%s?"
		for k in self.request.GET.keys():
			if (k != 'user' and self.request.GET[k] != ''):
				urlparams += "&" + k + "=" + self.request.GET[k]
		# Falls dieUsernr leer ist, kommmen wir von der Rollensicht des Panels, weil dort die Usernummer egal ist.
		# Die Nummer ist nur gesetzt wen wir auf der Standard-Factory aufgerufen werden.
		if usernr == "":
			url = urlparams % reverse('user_rolle_af')
		else:
			url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
		return url
class UhRUpdate(UpdateView):
	"""Ändert die Zuordnung von Rollen zu einem User."""
	# ToDo: Hierfür gibt es noch keine Buttons. Das ist noch über "Change" inkonsistent abgebildet
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
	Finde alle relevanten Informationen zur aktuellen Selektion: UserIDs und zugehörige Orga

	Ausgangspunkt ist TblUseridUndName.
	Hierfür gibt es einen Filter, der per GET abgefragt wird.
	Geliefert werden nur die XV-Nummern zu den Namen (diese muss es je Namen zwingend geben)

	Die dort gefundene Treffermenge wird angereichert um die relevanten Daten aus TblUserHatRolle.
	Hier werden allerdings alle UserIDen zurückgeliefert je Name.
	Von dort aus gibt eine ForeignKey-Verbindung zu TblRollen.

	Problematisch ist noch die Verbindung zwischen TblRollen und TblRollaHatAf,
	weil hier der Foreign Key per Definition in TblRolleHatAf liegt.
	Das kann aber aufgelöst werden,
	sobald ein konkreter User betrachtet wird und nicht mehr eine Menge an Usern.

	:param request: GET oder POST Request vom Browser
	:return: name_liste, panel_liste, panel_filter
	"""
	panel_liste = TblUserIDundName.objects.filter(geloescht=False).order_by('name')
	panel_filter = UseridFilter(request.GET, queryset=panel_liste)

	namen_liste = panel_filter.qs.filter(userid__istartswith="xv").select_related("orga")
	# panel_liste = panel_filter.qs.filter(userid__istartswith="xv").select_related("orga")

	"""
	# Ein paar Testzugriffe über das komplette Modell
	#   Hier ist die korrekte Hierarchie abgebildet von UserID bis AF:
	#   TblUserIDundName enthält Userid
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

	return (namen_liste, panel_filter)

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
	(namen_liste, panel_filter) = UhR_erzeuge_listen(request)
	return (namen_liste, panel_filter, rollen_liste, rollen_filter)

def UhR_erzeuge_listen_mit_rollen(request):
	"""
	Liefert zusätzlich zu den Daten aus UhR_erzeuge_listen noch die dazu gehörenden Rollen.
	Ausgangspunkt sind die Rollen, nach denen gesucht werden soll.
	Daran hängen UserIDs, die wiederum geeignet gefilter werden nach den zu findenden Usern

	Geliefert wird
	- die Liste der selektiert Namen (unabhängig davon, ob ihnen AFen oder Rollen zugewiesen sind)
	- den Panel_filter für korrekte Anzeige
	- Die Liste der Rollen, die in der Abfrage derzeit relevant sind
	- der Rollen_filter, der benötigt wird, um das "Rolle enthält"-Feld anzeigen lassen zu können
	:param request
	:return: namen_liste, panel_filter, rollen_liste, rollen_filter
	"""

	# Hole erst mal die Menge an Rollen, die namentlich passen
	suchstring = request.GET.get('rollenname', 'nix')
	if suchstring == "*":
		rollen_liste = TblUserhatrolle.objects.all().order_by('rollenname')
	else:
		rollen_liste = TblUserhatrolle.objects\
			.filter(rollenname__rollenname__icontains = suchstring)\
			.order_by('rollenname')
	rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

	(namen_liste, panel_filter) = UhR_erzeuge_listen(request)

	return (namen_liste, panel_filter, rollen_liste, rollen_filter)

def hole_userids_zum_namen(selektierter_name):
	"""
	Hole alle UserIDs, die zu dem ausgesuchten User passen.
	Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
	Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen

	:param selektierter_name: Zu welcehm Namen sollen die UserIDs gesucht werden?
	:return: Liste der UserIDs (als String[])
	"""
	userids = []	# Die Menge der UserIDs, die an Identität ID hängen

	# Wir müssen das in einer Schleife machen, weil wir von jedem Identitäts--Element nur die UserID benötigen
	number_of_userids = TblUserIDundName.objects \
		.filter(name=selektierter_name) \
		.filter(geloescht=False) \
		.count()
	for num in range(number_of_userids):
		userids.append(TblUserIDundName.objects
								.filter(name=selektierter_name)
								.order_by('-userid') \
								.filter(geloescht=False)[num].userid)
	return userids

# Selektiere die erforderlichen User- und Berechtigungsdaten
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
		selektierte_userids = hole_userids_zum_namen(selektierter_name)

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
		afliste = TblUserIDundName.objects.get(id=id).tblgesamt_set.all()  # Das QuerySet
		for e in afliste:
			if not e.geloescht: # Bitte nur die Rechte, die nicht schon gelöscht wurden
				afmenge.add(e.enthalten_in_af)  # AF der Treffermenge in die Menge übernehmen (Wiederholungsfrei)

		# Erzeuge zunächst die Hashes für die UserIDs.
		# Daran werden nachher die Listen der Rechte gehängt.
		for uid in selektierte_userids:
			afmenge_je_userID[uid] = set()

		# Selektiere alle Arbeitsplatzfunktionen, die derzeit mit den konkreten UserIDs verknüpft sind.
		for uid in selektierte_userids:
			tmp_afliste = TblUserIDundName.objects.get(userid = uid).tblgesamt_set.filter(geloescht = False)
			for e in tmp_afliste:
				afmenge_je_userID[uid].add(e.enthalten_in_af)  # Element an das UserID-spezifische Dictionary hängen
	else:
		userHatRolle_liste = []
		selektierter_name = -1
		selektierte_haupt_userid = 'keine_userID'

	return (userHatRolle_liste, selektierter_name, userids, usernamen,
			selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID)

def hole_rollen_zuordnungen(af_dict):
	"""
	Liefert eine Liste der Rollen, in denen eine Menge von AFs vorkommt,
	sortiert nach Zuordnung zu einer Liste an UserIDs

	:param af_dict: Die Eingabeliste besteht aus einem Dictionary af_dict[Userid] = AF_Menge_zur_UserID[]
	:return: vorhanden = Liste der Rollen, in denen die AF vorkommt und die dem Namen zugeordnet sind
	:return: optional = Liste der Rollen, in denen die AF vorkommt und die dem User nicht zugeordnet sind
	"""
	# Die beiden Ergebnislisten
	vorhanden = {}
	optional = {}

	# Eingangsparameter ist eine Liste von Userids mit den zugehörenden Listen an AFen:
	for userid in af_dict:
		af_menge = af_dict[userid]

		for af in af_menge:
			# Für genau eine Kombination aus UserID und AF wird gesucht, ob sie als Rolle (oder mehrere Rollen)
			# bereits administriert ist: ex(istierende Rollen).
			# Zusätzlich werden alle Möglichkeiten der Administration angeboten,
			# die noch nicht genutzt wurden: opt(ionale Rollen).
			(ex, opt) = suche_rolle_fuer_userid_und_af(userid, af)
			tag = '!'.join((userid, af)) # Flache Datenstruktur für Template erforderlich
			vorhanden[tag] = ex
			optional[tag] = opt
	return (vorhanden, optional)

"""
Liefert die XV-Nummer zu einer UserID zurück (die Stammnummer der Identität zur UserID)
:param userid: Eine beliebige UserID einer Identität
:return: Die StammuserID der Identität
"""
stamm_userid = lambda userid : 'X' + userid[1:]

def suche_rolle_fuer_userid_und_af(userid, af):
	"""
	Liefere für einen AF einer UserID die Liste der dazu passenden Rollen.
	Auch hier wird unterscheiden zwischen den existierenden Rollen des Users
	und den optionalen Rollen.
	Wichtig ist hier die Unterscheidung zwischen der Identität (in unserem Fall UserIDen XV\d{5}
	und den unterschiedlichen UserIDen ([XABCD]V\d{5})
	:param userid: Die UserID, für die die AF geprüft werden soll
	:param af: Die AF, die geprüft werden soll
	:return: Tupel mit zwei Listen: den vorhandenen Rollen und den optionalen Rollen
		Wichtig bei den Liste ist, dass beide als letztes einen leeren String erhalten.
		Das stellt sicher, dass in der Template-Auflösung nicht die Chars einzeln angezeigt werden,
		wenn nur eine einzige Rolle gefunden wurde.
	"""

	# Hole erst mal die Menge an Rollen, die bei dieser AF und der UserID passen
	rollen = TblRollehataf.objects.filter(af__af_name = af)
	rollen_liste = [str(rolle) for rolle in rollen]

	# Dann hole die Rollen, die dem User zugewiesen sind
	userrollen = TblUserhatrolle.objects\
		.filter(userid = stamm_userid(userid))\
		.order_by('rollenname')

	# Sortiere die Rollen, ob sie dem dem User zugeordnet sind oder nicht
	vorhanden = [str("{}!{}".format(einzelrolle.userundrollenid, einzelrolle.rollenname))\
				 for einzelrolle in userrollen\
				 if str(einzelrolle.rollenname) in rollen_liste
				]

	# Mengenoperation: Die Differenz zwischen den Rollen, die zur AF gehören und den Rollen, die der User bereits hat,
	# ist die Menge der Rollen, die als optional ebenfalls für die AF genutzt werden kann.
	# Leider sind "rollen_liste" und "vorhanden" inzwischen in verschiedenen Formaten,
	# deshalb geht die einfache Mengendifferenzbildung nicht mehr.
	optional = set(rollen_liste)
	for s in set(vorhanden):
		optional.discard(s.split('!')[1])
	optional = list(optional)
	optional.sort()
	vorhanden.append('') # Das hier sind die beiden Leerstrings am Ende der Liste
	optional.append('')
	return (vorhanden, optional)

def hole_af_mengen(userids, gesuchte_rolle):
	"""
	Hole eine Liste mit AFen, die mit der gesuchten Rolle verbunden sind.
	Erzeuge die Liste der AFen, die mit den UserIDs verbunden sind
	und liefere die Menge an AFen, die beiden Kriterien entsprechen.
	Für die Anzeige im Portal liefert die Funktion eine möglichst flache Datenstruktur.
	:param userids: Dictionary mit Key = Name der Identität und val = Liste der UserIDs der Identität
					(Beispiel: userids['Eichler, Lutz'] = ['XV13254])
	:param gesuchte_rolle: Wenn None, suche nach allen Rollen, sonst filtere nach dem Suchstring (icontains).
					gesuchte_rolle wird als None übergeben, wenn der Suchstring "*" verwendet wurde
	:return: af_dict{}[UserID] = AF[]

	"""

	such_af = set()
	if gesuchte_rolle is None:
		rollen_liste = TblRollehataf.objects.all()
	else:
		rollen_liste = TblRollehataf.objects.filter(rollenname__rollenname__icontains = gesuchte_rolle)

	for rolle in rollen_liste: # Filtere mehrfach gefundene Elemente heraus (django hat kein echtes group by)
		such_af.add(rolle.af)

	af_dict = {}
	for name in dict(userids):
		for userid in userids[name]:
			if gesuchte_rolle is None: # Finde alle AFen zur UserID
				af_liste = TblGesamt.objects.filter(userid_name_id__userid = userid).filter(geloescht = False)
			else:
				af_liste = TblGesamt.objects.filter(userid_name_id__userid = userid).\
					filter(geloescht = False)\
					.filter(enthalten_in_af__in = such_af)

			af_menge = set([af.enthalten_in_af for af in af_liste])
			af_dict[userid] = af_menge
	return af_dict

def UhR_hole_rollengefilterte_daten(namen_liste, gesuchte_rolle):
	"""
	Finde alle UserIDs, die über die angegebene Rolle verfügen.
	Wenn gesuchte_rolle is None, dann finde alle Rollen.

	Erzeuge die Liste der UserIDen, die mit den übergebenen Namen zusammenhängen
	Dann erzeuge die Liste der AFen, die mit den UserIDs verbunden sind
	- Notiere für jede der AFen, welche Rollen Grund für diese AF derzeit zugewiesen sind (aus UserHatRolle)
	- Notiere, welche weiteren Rollen, die derzeit nicht zugewiesen sind, für diese AF in Frage kämen

	Liefert die folgende Hash-Liste zurück:
	Rollenhash{}[(Name, UserID, AF)] = (
		(liste der vorhandenen Rollen, in denen die AF enthalten ist),
		(liste weiterer Rollen, in denen die AF enthalten ist)
		)

	Liefert die Namen / UserID-Liste zurück
	userids{}[Name] = (Userids zu Name, alfabeitsch absteigend sortiert: XV, DV, CV, BV, AV)

	:param namen_liste: Zu welchen Namen soll die Liste erstellt werden?
	:param gesuchte_rolle: s.o.
	:return: (rollenhash, userids)
	"""
	userids = {}
	for name in namen_liste:
		userids[name.name] = hole_userids_zum_namen(name.name)
		# print ('UserIDs zum Namen {}: {}'.format(name.name, userids[name.name]))

	af_dict = hole_af_mengen(userids, gesuchte_rolle)
	(vorhanden, optional) = hole_rollen_zuordnungen(af_dict)
	return (userids, af_dict, vorhanden, optional)

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

# Die beiden nachfolgenden Funktionen dienen nur dem Aufruf der eigentlichen Konzept-Funktion
def panel_UhR_konzept_pdf(request):
	return erzeuge_UhR_konzept(request, False)

def panel_UhR_konzept(request):
	return erzeuge_UhR_konzept(request, True)

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
		(namen_liste, panel_filter, rollen_liste, rollen_filter) = UhR_erzeuge_listen_ohne_rollen(request)
		(userHatRolle_liste, selektierter_name, userids, usernamen,
		 selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID) \
			= UhR_hole_daten(namen_liste, id)
		(paginator, pages, pagesize) = pagination(request, namen_liste, 10000)

		form = ShowUhRForm(request.GET)
		context = {
			'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
			'filter': panel_filter, 'form': form,
			'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
			'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
			'userHatRolle_liste': userHatRolle_liste,
			'id': id,
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
		(namen_liste, panel_filter, rollen_liste, rollen_filter) =\
			UhR_erzeuge_listen_mit_rollen(request)

		gesuchte_rolle = request.GET.get('rollenname', None)
		if gesuchte_rolle == "*":	# Das ist die Wildcard-Suche, um den Modus in der Oberfläche auszuwählen
			gesuchte_rolle = None

		(userids, af_per_uid, vorhanden, optional) = UhR_hole_rollengefilterte_daten(namen_liste, gesuchte_rolle)

		form = ShowUhRForm(request.GET)
		context = {
			'filter': panel_filter, 'form': form,
			'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
			'userids': userids,
			'af_per_uid': af_per_uid,
			'vorhanden': vorhanden,
			'optional': optional,
			'version': version,
		}
		return render(request, 'rapp/panel_UhR_rolle.html', context)
class AFListenUhr(UhR):
	def behandle(self, request, id):
		assert 0, 'Funktion AFListenUhr::behandle() ist noch nicht implementiert. Der Aufruf ist nicht valide.'

# Zeige das Selektionspanel
def panel_UhR(request, id = 0):
	"""
	Finde die richtige Anzeige und evaluiere sie über das factory-Pattern

	- wenn rollennamme gesetzt ist, rufe die Factory "rolle"
	- wenn rollenname nicht gesetzt oder leer ist und afname gesetzt ist, rufe factory "af"
	- Ansonsten rufe die Standard-Factory "einzel"

	:param request: GET oder POST Request vom Browser
	:param pk: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
	:return: Gerendertes HTML
	"""
	assert request.method != 'POST', 'Irgendwas ist im panel_UhR über POST angekommen'
	assert request.method == 'GET', 'Irgendwas ist im panel_UhR nicht über GET angekommen: ' + request.method

	if 'afname' in request.GET.keys(): print (request.GET['afname'])

	if request.GET.get('rollenname', None) != None and request.GET.get('rollenname', None) != "":
		name = 'rolle'
	elif 'afname' in request.GET.keys() and request.GET['afname'] != None and request.GET['afname'] != "":
		print ('Factory AF')
		name = 'af'
	else:
		name = 'einzel'

	obj = UhR.factory(name)
	return obj.behandle(request, id)

def erzeuge_pdf_namen(request):
	zeit = str(timezone.now())[:10]
	return 'Berechtigungskonzept_{}_{}.pdf'.format(zeit, request.GET.get('gruppe', ''))

# Erzeuge das Berechtigungskonzept für Anzeige und PDF
def	erzeuge_UhR_konzept(request, ansicht):
	"""
	Erzeuge das Berechtigungskonzept für eine Menge an selektierten Identitäten.

	:param request: GET Request vom Browser
	:param ansicht: Flag, ob die Daten als HTML zur Ansicht oder als PDF zum Download geliefert werden sollen
	:return: Gerendertes HTML
	"""

	# Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
	(namen_liste, panel_filter) = UhR_erzeuge_listen(request)

	if request.method == 'GET':
		(rollenMenge, userids, usernamen) = UhR_verdichte_daten(namen_liste)
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
		filename = erzeuge_pdf_namen(request)
		content = "inline; filename={}".format(filename)
		download = request.GET.get("download")
		if download:
			content = "attachment; filename={}".format(filename)
		response['Content-Disposition'] = content
		return response
	return HttpResponse("Fehlerhafte PDF-Generierung in erzeuge_UhR_konzept")

# Funktionen zum Erstellen des Funktionsmatrix
def erzeuge_UhR_matrixdaten(panel_liste):
	"""
	Überschriften-Block:
		Erste Spaltenüberschrift ist "Name" als String, darunter werden die Usernamen liegen, daneben:
			Zeige Teamzugehörigkeit(en), daneben
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
	teams_je_username = {} # Derzeit nur ein Team/UserID, aber multi-Teams müssen vorbereitet werden

	for row in panel_liste:
		usernamen.add(row.name)
		teamliste = TblOrga.objects\
			.filter(tbluseridundname__name = row.name) \
			.exclude(team = "Gelöschter User") # Die als gelöscht markierten User werden nicht mehr angezeigt

		teammenge = set()
		for team in teamliste:
			teammenge.add(str(team))
		teams_je_username[row.name] = [ str(team) for team in teammenge ]

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
	return (sorted(usernamen), sorted(list(rollenmenge), key=order), rollen_je_username, teams_je_username)

def panel_UhR_matrix(request):
	"""
	Erzeuge eine Verantwortungsmatrix für eine Menge an selektierten Identitäten.

	:param request: GET Request vom Browser
	:return: Gerendertes HTML
	"""

	# Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
	(namen_liste, panel_filter) = UhR_erzeuge_listen(request)

	if request.method == 'GET':
		(usernamen, rollenmenge, rollen_je_username, teams_je_username) = erzeuge_UhR_matrixdaten(namen_liste)
	else:
		(usernamen, rollenmenge, rollen_je_username, teams_je_username) = (set(), set(), set(), {})

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
		'teams_je_username': teams_je_username,
		'version': version,
	}
	return render(request, 'rapp/panel_UhR_matrix.html', context)

def panel_UhR_matrix_csv(request, flag = False):
	"""
	Exportfunktion für das Filter-Panel zum Selektieren aus der "User und Rollen"-Tabelle).
	:param request: GET oder POST Request vom Browser
	:param flag: False oder nicht gegeben -> liefere ausführliche Text, 'kommpakt' -> liefere nur Anfangsbuchstaben
	:return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
	"""
	if request.method != 'GET':
		return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_matrix_csv")

	(namen_liste, panel_filter) = UhR_erzeuge_listen(request)
	(usernamen, rollenmenge, rollen_je_username, _) = erzeuge_UhR_matrixdaten(namen_liste) # Ignoriere teamliste im PDF

	response = HttpResponse(content_type="text/csv")
	response['Content-Disposition'] = 'attachment; filename="matrix.csv"' # ToDo Hänge Datum an Dateinamen an
	response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)

	headline = [smart_str(u'Name')]
	for r in rollenmenge:
		headline += [smart_str(r.rollenname)]

	writer = csv.writer(response, csv.excel, delimiter = ',', quotechar = '"')
	writer.writerow(headline)

	for user in usernamen:
		line = [user]
		for rolle in rollenmenge:
			if flag:
				wert = finde(rollen_je_username[user], rolle)
				if wert == None or len(wert) <= 0:
					line += ['']
				else:
					line += [smart_str(wert[0])]
			else:
				line += [smart_str(finde(rollen_je_username[user], rolle))]
		writer.writerow(line)

	return response

def panel_UhR_af_export(request, id):
	"""
	Exportfunktion für das Filter-Panel aus der "User und Rollen"-Tabelle).
	:param request: GET Request vom Browser
	:return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
	"""
	if request.method != 'GET':
		return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_af_export")

	(namen_liste, panel_filter, rollen_liste, rollen_filter) = UhR_erzeuge_listen_ohne_rollen(request)
	(userHatRolle_liste, selektierter_name, userids, usernamen,
	 selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID) \
		= UhR_hole_daten(namen_liste, id)

	"""
	context = {
		'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
		'filter': panel_filter, 'form': form,
		'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
		'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
		'userHatRolle_liste': userHatRolle_liste,
		'id': id,
		'selektierter_name': selektierter_name,
		'selektierte_userid': selektierte_haupt_userid,
		'selektierte_userids': selektierte_userids,
		'afmenge_je_userID': afmenge_je_userID,
		'version': version,
	}
	"""
	response = HttpResponse(content_type="text/csv")
	response['Content-Disposition'] = 'attachment; filename="rollen.csv"'
	response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)

	headline = [
		smart_str(u'Name'),
		smart_str(u'Rollenname'),
		smart_str(u'AF'),
		smart_str(u'Mussrecht')
	]
	for userid in selektierte_userids:
		headline.append(smart_str(userid))
	print (headline)

	writer = csv.writer(response, csv.excel, delimiter = ',', quotechar = '"')
	writer.writerow(headline)

	for rolle in userHatRolle_liste:
		for rollendefinition in TblRollehataf.objects.filter(rollenname = rolle.rollenname):
			line = [selektierter_name, rolle.rollenname, rollendefinition.af]
			if rollendefinition.mussfeld > 0: line.append('ja')
			else: line.append('nein')
			for userid in selektierte_userids:
				print(line, userid)
				if str(rollendefinition.af) in afmenge_je_userID[userid]: line.append('ja')
				else: line.append('nein')
			writer.writerow(line)

	return response
