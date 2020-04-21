from __future__ import unicode_literals

from django.http import HttpResponse
from django.urls import reverse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.utils.encoding import smart_str
from django.db.models import Count

from django.db import connection

from .excel import Excel
import csv
import re

from .filters import RollenFilter, UseridFilter
from .xhtml2 import render_to_pdf

from .views import version, pagination
from .forms import ShowUhRForm, CreateUhRForm, ImportForm, ImportFormSchritt3
from .models import TblUserIDundName
from .models import TblGesamt
from .models import TblRollen
from .models import TblRollehataf
from .models import TblUserhatrolle
from .models import TblOrga
from .models import TblAfliste
from .models import RACF_Rechte
from .models import TblDb2
from .models import TblUebersichtAfGfs
from .models import ACLGruppen

from .templatetags.gethash import finde
from django.utils import timezone

from copy import deepcopy


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

    # fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

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
        usernr = self.request.GET.get('user', 0)  # Sicherheitshalber - falls mal kein User angegeben ist

        urlparams = "%s?"
        for k in self.request.GET.keys():
            if (k != 'user' and self.request.GET[k] != ''):
                urlparams += "&" + k + "=" + self.request.GET[k]
        url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
        return url


class UhRDelete(DeleteView):
    """Löscht die Zuordnung einer Rolle zu einem User."""
    model = TblUserhatrolle
    template_name = 'rapp/uhr_confirm_delete.html'

    # Nach dem Löschen soll die vorherige Selektion im Panel "User und Rollen" wieder aktualisiert gezeigt werden.
    # Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzten Suchparameter benötigt.
    def get_success_url(self):
        usernr = self.request.GET.get('user', "0")  # Sicherheitshalber - falls mal kein User angegeben ist

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
        usernr = self.request.GET.get('user', 0)  # Sicherheitshalber - falls mal kein User angegeben ist

        urlparams = "%s?"
        for k in self.request.GET.keys():
            if (k != 'user' and self.request.GET[k] != ''):
                urlparams += "&" + k + "=" + self.request.GET[k]
        url = urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})
        return url


def UhR_erzeuge_gefiltere_namensliste(request):
    """
    Finde alle relevanten Informationen zur aktuellen Selektion: UserIDs und zugehörige Orga

    Ausgangspunkt ist TblUseridUndName.
    Hierfür gibt es einen Filter, der per GET abgefragt wird.
    Geliefert werden nur die XV-Nummern zu den Namen (diese muss es je Namen zwingend geben)

    Die dort gefundene Treffermenge wird angereichert um die relevanten Daten aus TblUserHatRolle.
    Hier werden alle UserIDen zurückgeliefert je Name.
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

    teamnr = request.GET.get('orga')
    if teamnr != None and teamnr != '':
        teamqs = TblOrga.objects.get(id=teamnr)
        if teamqs.teamliste != None \
                and teamqs.freies_team != None \
                and teamqs.teamliste != '' \
                and teamqs.freies_team != '':
            print("""Fehler in UhR_erzeuge_gefiltere_namensliste: \
            Sowohl teamliste als auch freies_team sind gesetzt in Team {}: teammliste = {}, freies_team = {}."""
                  .format(teamnr, teamqs.teamliste, teamqs.freies_team))
            return (namen_liste, panel_filter)
        if teamqs.teamliste != None and teamqs.teamliste != '':
            namen_liste = behandle_teamliste(panel_liste, request, teamqs)
        elif teamqs.freies_team != None and teamqs.freies_team != '':
            namen_liste = behandle_freies_team(panel_liste, request, teamqs)

    """
    # Ein paar Testzugriffe über das komplette Modell
    #   Hier ist die korrekte Hierarchie abgebildet von UserID bis AF:
    #   TblUserIDundName enthält Userid
    #       TblUserHatRolle hat Foreign Key 'userid' auf TblUserIDundName
    #       -> tbluserhatrolle_set.all auf eine aktuelle UserID-row liefert die Menge der relevanten Rollen
    #           Rolle hat ForeignKey 'rollenname' auf TblRolle und erhält damit die nicht-User-spezifischen Rollen-Parameter
    #               TblRolleHatAF hat ebenfalls einen ForeignKey 'rollennname' auf TblRollen
    #               -> rollenname.tblrollehataf_set.all liefert für eine konkrete Rolle die Liste der zugehörigen AF-Detailinformationen
    #
    #        TblGesamt hat FK 'userid_name' auf TblUserIDundName
    #        -> .tblgesamt_set.filter(geloescht = False) liefert die aktiven Arbeitsplatzfunktionen
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


def behandle_freies_team(panel_liste, request, teamqs):
    """
    Wenn in der tblOrga für die aktuelle Selektion ein Freies_Team eingetragen ist,
    müssen an dieser Stelle zunächst die angegebenen Namen berücksichtigt werden.
    Die Anzeigeinhalte werden dann später bearbeitet.
    :param panel_liste: Das bisherige Panel-QS
    :param request: Das Übliche
    :param teamqs: Hieran hängt in dieser Funktion der Inhalt "freies_team"
    :return: gefilterte Namensliste als QuerySet
    """
    eintraege = teamqs.freies_team.split('|')
    user = []
    for e in eintraege:
        user += [e.split(':')[0]]  # erster Teil ist der Name, zweiter Teil die gewünschte Anzeige
    print('gesuchte User =', user)
    namen_liste = panel_liste.filter(name__in=user)
    return behandle_ft_oder_tl(namen_liste, request)


def behandle_teamliste(panel_liste, request, teamqs):
    """
    Wenn in der tblOrga für die aktuelle Selektion eine Teamliste eingetragen ist,
    müssen an dieser Stelle die angegebenen Namen berücksichtigt werden.
    :param panel_liste: Das bisherige Panel-QS
    :param request: Das Übliche
    :param teamqs: Hieran hängt in dieser Funktion der Inhalt "teamliste"
    :return: gefilterte Namensliste als QuerySet
    """
    teamliste = teamqs.teamliste.split(',')
    # print('Teamliste =', teamliste)
    namen_liste = panel_liste.filter(orga__team__in=teamliste)
    return behandle_ft_oder_tl(namen_liste, request)


def behandle_ft_oder_tl(namen_liste, request):
    """
    In den rufenden Funktionen wurde bereits eine Namensliste erstellt.
    Diese muss nun allerdings noch weiter gefiltert werden,
    falls eine Namensteil oder eine Gruppe als Filterkriterien angegeben wurden.
    Dabei können nicht die normalen Filterfunktionen verwendet werden, weil ja die Angabe
    freies_teamm oder teamliste ghenau den anderen Filterkritereien widersprechen könnten.
    Außerdem werden von dieser Funktion nur XV-Nummern-Einträge zurückgeliefert,
    das vereinfacht das weitere Vorgehen erheblich.

    :param namen_liste: Die besher gefundenen Namen als QuerySet
    :param request: Das Übliche
    :return: Die möglicherweise weiter gefilterte Nanemsliste
    """
    name = request.GET.get('name')
    gruppe = request.GET.get('gruppe')
    # print('gefundene namen_liste vor Filterung =', namen_liste)
    if gruppe != None and gruppe != '':
        # print('Filtere nach Gruppe', gruppe)
        namen_liste = namen_liste.filter(gruppe__icontains=gruppe)
        # print(namen_liste)
    if name != None and name != '':
        # print('Filtere nach Name', name)
        namen_liste = namen_liste.filter(name__istartswith=name)
        # print(namen_liste)
    namen_liste = namen_liste.filter(userid__istartswith="xv").select_related("orga")
    # print('Letztendliche Liste der Namen:', namen_liste)
    return namen_liste


def UhR_erzeuge_listen_ohne_rollen(request):
    """
    Liefert zusätzlich zu den Daten aus UhR_erzeuge_gefiltere_namensliste noch eine leere Rollenliste,
    damit das Suchfeld angezeigt wird
    :param request:
    :return: namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter
    """

    # Hole erst mal eine leere Rollenliste ud dazu passenden Filter
    rollen_liste = TblUserhatrolle.objects.none()
    rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

    # Und nun die eigentlich wichtigen Daten holen
    (namen_liste, panel_filter) = UhR_erzeuge_gefiltere_namensliste(request)
    return (namen_liste, panel_filter, rollen_liste, rollen_filter)


def UhR_erzeuge_listen_mit_rollen(request):
    """
    Liefert zusätzlich zu den Daten aus UhR_erzeuge_gefiltere_namensliste noch die dazu gehörenden Rollen.
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
    if suchstring == "*" or suchstring == "-":
        rollen_liste = TblUserhatrolle.objects.all().order_by('rollenname').order_by('rollenname')
    else:
        rollen_liste = TblUserhatrolle.objects \
            .filter(rollenname__rollenname__icontains=suchstring) \
            .order_by('rollenname')
    rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

    (namen_liste, panel_filter) = UhR_erzeuge_gefiltere_namensliste(request)

    return (namen_liste, panel_filter, rollen_liste, rollen_filter)


def hole_unnoetigte_afen(namen_liste):
    """
    Diese Funktion dient dazu, überflüssige AFen in Rollendefinitionen zu erkennen
    Erzeuge Deltaliste zwischen der Sollvorgabe der Rollenmenge
    und der Menge der vorhandenen Arbeitsplatzfunktionen.

    :param namen_liste: Liste der Namen, die derzeit selektiert sind.
    :return: Queryset mit Treffern, beinhaltet Rollennamen und AF
    """

    # Zunächst wird das Soll der User-Rollen ermittelt
    soll_rollen = TblUserhatrolle.objects \
        .filter(userid__name__in=namen_liste.values('name')) \
        .values('userid__name', 'rollenname')

    # Nun das Ist der AFen je User:
    ist_afen = TblGesamt.objects \
        .exclude(geloescht=True) \
        .exclude(userid_name__geloescht=True) \
        .filter(userid_name__name__in=namen_liste.values('name')) \
        .values('enthalten_in_af').annotate(dcount=Count('enthalten_in_af'))

    # Und das Delta: Ziehe alle IST-AFen von den Soll-AFen ab und liefere das Delta zurück
    delta = TblRollehataf.objects \
        .filter(rollenname__in=soll_rollen.values('rollenname')) \
        .exclude(af__af_name__in=ist_afen.values('enthalten_in_af')) \
        .order_by('rollenname__rollenname', 'af', ) \
        .values(
        'rollenname__rollenname',
        'af__af_name',
    )

    return delta


def hole_userids_zum_namen(selektierter_name):
    """
    Hole alle UserIDs, die zu dem ausgesuchten User passen.
    Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
    Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen

    :param selektierter_name: Zu welcehm Namen sollen die UserIDs gesucht werden?
    :return: Liste der UserIDs (als String[])
    """
    userids = []  # Die Menge der UserIDs, die an Identität ID hängen

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
    usernamen = set()  # Die Namen aller User,  die in der Selektion erfasst werden
    userids = set()  # Die UserIDs aller User,  die in der Selektion erfasst werden
    afmenge = set()  # Die Menge aller AFs aller mit ID spezifizierten User (für Berechtigungskonzept)
    selektierte_userids = set()  # Die Liste der UserIDs, die an Identität ID hängen
    afmenge_je_userID = {}  # Menge mit UserID-spezifischen AF-Listen

    for row in panel_liste:
        usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
        userids.add(row.userid)

    if (id != 0):  # Dann wurde der ReST-Parameter 'id' mitgegeben

        userHatRolle_liste = TblUserhatrolle.objects.filter(userid__id=id).order_by('rollenname')
        selektierter_name = TblUserIDundName.objects.get(id=id).name

        # Wahrscheinlich werden verschiedene Panels auf die Haupt-UserID referenzieren (die XV-Nummer)
        selektierte_haupt_userid = TblUserIDundName.objects.get(id=id).userid

        # Hole alle UserIDs, die zu dem ausgesuchten User passen.
        selektierte_userids = hole_userids_zum_namen(selektierter_name)

        # Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
        afliste = TblUserIDundName.objects.get(id=id).tblgesamt_set.all()  # Das QuerySet
        for e in afliste:
            if not e.geloescht:  # Bitte nur die Rechte, die nicht schon gelöscht wurden
                afmenge.add(e.enthalten_in_af)  # AF der Treffermenge in die Menge übernehmen (Wiederholungsfrei)

        # Erzeuge zunächst die Hashes für die UserIDs.
        # Daran werden nachher die Listen der Rechte gehängt.
        for uid in selektierte_userids:
            afmenge_je_userID[uid] = set()

        # Selektiere alle Arbeitsplatzfunktionen, die derzeit mit den konkreten UserIDs verknüpft sind.
        for uid in selektierte_userids:
            tmp_afliste = TblUserIDundName.objects.get(userid=uid).tblgesamt_set.filter(geloescht=False)
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
            tag = '!'.join((userid, af))  # Flache Datenstruktur für Template erforderlich
            vorhanden[tag] = ex
            optional[tag] = opt
    return (vorhanden, optional)


"""
Liefert die XV-Nummer zu einer UserID zurück (die Stammnummer der Identität zur UserID)
:param userid: Eine beliebige UserID einer Identität
:return: Die StammuserID der Identität
"""
stamm_userid = lambda userid: 'X' + userid[1:]


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
    rollen = TblRollehataf.objects.filter(af__af_name=af)
    rollen_liste = [str(rolle) for rolle in rollen]

    # Dann hole die Rollen, die dem User zugewiesen sind
    userrollen = TblUserhatrolle.objects \
        .filter(userid=stamm_userid(userid)) \
        .order_by('rollenname')

    # Sortiere die Rollen, ob sie dem dem User zugeordnet sind oder nicht
    vorhanden = [str("{}!{}".format(einzelrolle.userundrollenid, einzelrolle.rollenname)) \
                 for einzelrolle in userrollen \
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
    vorhanden.append('')  # Das hier sind die beiden Leerstrings am Ende der Liste
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
                    Ist die gesuchte Rolle "-", dann filtere nach unzugewiesenen AFen.
                    gesuchte_rolle wird als None übergeben, wenn der Suchstring "*" verwendet wurde
    :return: af_dict{}[UserID] = AF[]

    """

    such_af = liefere_af_zu_rolle(gesuchte_rolle)

    af_dict = {}
    for name in dict(userids):
        for userid in userids[name]:  # Die erste UserID ist die XV-Nummer
            if gesuchte_rolle is None:  # Finde alle AFen zur UserID
                af_liste = TblGesamt.objects.filter(userid_name_id__userid=userid).filter(geloescht=False)

            elif gesuchte_rolle == "-":  # Finde alle AFen zur UserID, die nicht Rollen zugeordnet sind
                bekannte_rollen = TblUserhatrolle.objects.filter(userid=userids[name][0]).values('rollenname')

                suche_nach_none_wert(bekannte_rollen)  # Irgendwelche Merkwürdigkeiten?
                unerwuenschte_af = TblRollehataf.objects.filter(rollenname__in=bekannte_rollen) \
                    .exclude(af__af_name=None) \
                    .values('af__af_name')

                af_liste = TblGesamt.objects.filter(userid_name_id__userid=userid) \
                    .filter(geloescht=False) \
                    .exclude(enthalten_in_af__in=unerwuenschte_af)
            else:
                af_liste = TblGesamt.objects.filter(userid_name_id__userid=userid) \
                    .filter(geloescht=False) \
                    .filter(enthalten_in_af__in=such_af)

            af_menge = set([af.enthalten_in_af for af in af_liste])
            af_dict[userid] = af_menge
    return af_dict


def hole_alle_offenen_AFen_zur_userid(userid, erledigt):
    """
    Liefert eine Menge aller AFen, die für eine UserID in der Gesamttabelle aufgeführt sind
    und die nicht in der erledigt-Liste auftauchen
    :param userid:
    :return: QuerySet mit den gesuchten AFen
    """
    print('erledigt Anzahl = {}\n Inhalt ='.format(erledigt.count(), list(erledigt)))
    print('ungefilterte Gesamtliste = ',
          list(TblGesamt.objects
               .exclude(geloescht=True)
               .exclude(userid_name_id__geloescht=True)
               .filter(userid_name_id__userid=userid)
               .values('enthalten_in_af')
               .distinct()
               .order_by('enthalten_in_af')
               ))
    print('Länge der Gesamtliste = ',
          TblGesamt.objects
          .exclude(geloescht=True)
          .exclude(userid_name_id__geloescht=True)
          .filter(userid_name_id__userid=userid)
          .values('enthalten_in_af')
          .distinct()
          .count()
          )
    af_qs = TblGesamt.objects \
        .exclude(geloescht=True) \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(enthalten_in_af__in=erledigt) \
        .filter(userid_name_id__userid=userid) \
        .values('enthalten_in_af') \
        .distinct() \
        .order_by('enthalten_in_af')
    print('AF_QS Anzahl = {}, Inhalt = {}'.format(af_qs.count(), list(af_qs)))
    return af_qs


def liefere_af_zu_rolle(gesuchte_rolle):
    """
    Hole die Einträge in TblRolleHatAF, die zu einer angegebenen Rolle passen.
    Wurde None oder "-" als Rollenname übergeben, liefere die Liste für alle Rollen.
    :param gesuchte_rolle: EIN Rollenname oder None oder "-"
    :return: Trefferergebnis der Abfrage
    """
    if gesuchte_rolle is None or gesuchte_rolle == "-":
        such_af = TblRollehataf.objects.all() \
            .values('af__af_name') \
            .distinct() \
            .order_by('af__af_name')
    else:
        such_af = TblRollehataf.objects \
            .filter(rollenname__rollenname__icontains=gesuchte_rolle) \
            .values('af__af_name') \
            .distinct() \
            .order_by('af__af_name')
    return such_af


def hole_soll_af_mengen(rollenmenge):
    """
    Hole für jede der übergebenen Rollen die SOLL-AFen.
    :param rollenmenge:
    :return: QUerySet mit den SOLL-AFen
    """
    retval = TblRollehataf.objects.none()

    for rolle in rollenmenge:
        retval |= liefere_af_zu_rolle(rolle)
    return retval


def suche_nach_none_wert(bekannte_rollen):
    """
    #Suche nach Einträgen in der Tabelle RolleHatAf, bei denen die AF None ist.
    :param bekannte_rollen:
    :return: True, wenn was gefunden wurde, sonst False
    """
    none_af = TblRollehataf.objects.filter(rollenname__in=bekannte_rollen).filter(af__af_name=None)
    if len(none_af) > 0:
        print('WARNING: Möglicherweise Irritierende Resultate, weil None in Suchmenge enthalten ist:')
        print('none_af:', len(none_af), none_af)
        print('Der Wert wurde in dieser Abfrage herausgefiltert, kann aber an andere Stelle irritieren.')
        print('Das entsteht, wenn als AF in einer Rolle "-----" selektiert wurde')
        return True
    return False


def UhR_hole_rollengefilterte_daten(namen_liste, gesuchte_rolle=None):
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

    af_dict = hole_af_mengen(userids, gesuchte_rolle)
    (vorhanden, optional) = hole_rollen_zuordnungen(af_dict)
    return (userids, af_dict, vorhanden, optional)


def freies_team(request):
    return not kein_freies_team(request)


def kein_freies_team(request):
    """
    Ist in der aktuellen Selektion ein Eintrag in der Teamdefinition "freies_team" gesetzt?
    :param request:
    :return: True, wenn "freies_feld" weder None noch '' ist
    """
    teamnr = request.GET.get('orga')
    if teamnr == None or teamnr == '':
        return True

    teamqs = TblOrga.objects.get(id=teamnr)
    return teamqs.freies_team == None or teamqs.freies_team == ''


def soll_komplett(request, row):
    """
    Liefere für einen konkreten User in row, ob für ihn die Komplettdarstellung erfolgen soll
    oder die eingeschränkte Sicht
    :param request: Für die Orga-Definition benötigt
    :param row: Der aktuelle User
    :return: True falls für den User die KOmmplettdarstellung erfolgen soll
    """
    teamnr = request.GET.get('orga')
    teamqs = TblOrga.objects.get(id=teamnr)
    assert (teamqs.freies_team != None)
    eintraege = teamqs.freies_team.split('|')
    for e in eintraege:
        zeile = e.split(':')
        if row.name.lower() == zeile[0].lower():
            if zeile[1].lower() == 'komplett':
                return True
            else:
                return False
    return False


# Funktionen zum Erstellen des Berechtigungskonzepts
def UhR_verdichte_daten(request, panel_liste):
    """
    Es gibt zunächst Fallunterscheidungen zu den Einträgen in der panel_liste:
    - Wenn kein Team gewählt wurde oder das gewählte Team kein "freies_team" ist
      oder es ein freies_team ist und der User-Name mit 'komplett' angegeben ist
        nimm die Standardbeaarbeitung
    - Wenn es sich um ein "freies_team" handelt und der User-Name nicht mit 'komplett' angegeben ist,
        wird die Spezialbehandlung durchgeführt
    """
    userids = set()
    usernamen = set()
    rollenmenge = set()

    for row in panel_liste:
        if row.userid[:2].lower() == "xv":
            # print('\n\nBehandle', row.name)
            if kein_freies_team(request) or soll_komplett(request, row):
                (rollenmenge, usernamen, userids) = verdichte_standardfall(rollenmenge, row, userids, usernamen)
            else:
                print('\nUhR_verdichte_daten: Start rollenmenge =', rollenmenge)
                (rollenmenge, usernamen, userids) = \
                    verdichte_spezialfall(rollenmenge, row, userids, usernamen, request)
                print('\nUhR_verdichte_daten: ergebnis rollenmenge =', rollenmenge)

    def order(a):
        return a.rollenname.lower()  # Liefert das kleingeschriebene Element, nach dem sortiert werden soll

    return (sorted(list(rollenmenge), key=order), userids, usernamen)


def verdichte_standardfall(rollenmenge, row, userids, usernamen):
    """
     Ausgehend von den Userids der Selektion zeige
      für den angebenen XV-User (nur die XV-User zeigen auf Rollen, deshalb nehmen wir nur diese)
        alle Rollen mit allen Details
          einschließlich aller darin befindlicher AFen mit ihren formalen Zuweisungen (Soll-Bild)
            verdichtet auf Mengenbasis
              (keine Doppelnennungen von Rollen,
              aber ggfs. Mehrfachnennungen von AFen,
              wenn sie in disjunkten Rollen mehrfach erscheinen)

    :param rollenmenge: Die bislang zusammengestellten Rollen
    :param row: Der aktuelle User
    :param userids: Die bislang behandelten UserIDs
    :param usernamen:
    :return: alle erweiterten Mengen: rollenmenge, usernamen, userids
    """
    usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
    userids.add(row.userid)
    userHatRollen = TblUserhatrolle.objects.filter(userid__userid=row.userid).order_by('rollenname')
    for e in userHatRollen:
        rollenmenge.add(e.rollenname)
    return (rollenmenge, usernamen, userids)


def verdichte_spezialfall(rollenmenge, row, userids, usernamen, request):
    """
    - Wenn es sich um ein "freies_team" handelt und der User-Name nicht mit 'komplett' angegeben ist
            - wird zunächst die in der übergebenen Rolle angegebene Liste bearbeitet:
            - wenn eine Rolle namens "Weitere <Gruppenbezeichnung des Users>" existiert,
                werden alle AFen daraus entfernt, sonst wird die Rolle erzeugt und dem User zugewiesen
            - Alle AFen des Users, die nicht bereits über rollenmenge adressiert sind, werden der neuen Rolle hinzugefügt
            - Die neu konfigurierte Rolle wird der Rollenmenge hinzugefügt

    :param rollenmenge: Die bislang zusammengestellten Rollen
    :param row: Der aktuelle User
    :param userids: Die bislang behandelten UserIDs
    :param usernamen:
    :return: alle erweiterten Mengen: rollenmenge, usernamen, userids
    """
    usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
    userids.add(row.userid)
    userHatRollen = TblUserhatrolle.objects.filter(userid__userid=row.userid).order_by('rollenname')

    assert (request.GET.get('orga') != None)
    spezialteam = TblOrga.objects.get(id=request.GET.get('orga'))
    erlaubte_rollenqs = TblUserhatrolle.objects \
        .filter(userid__name=row.name) \
        .filter(teamspezifisch=spezialteam)

    erlaubte_rollen = set()
    for e in erlaubte_rollenqs:
        # print('erlaubte Rollen hat gefunden:', e.rollenname)
        erlaubte_rollen.add(e.rollenname)
        rollenmenge.add(e.rollenname)

    print('verdichte_spezialfall: Rollenmenge nach Ergänzung erlaubte Rollen =', rollenmenge)

    restrolle = erzeuge_restrolle(row.userid, erlaubte_rollen, spezialteam)
    print('Restrolle =', restrolle)

    rollenmenge.add(restrolle)

    print('verdichte_spezialfall: Ergebnis Rollenmenge =', rollenmenge)
    return (rollenmenge, usernamen, userids)


def erzeuge_restrolle(userid, rollenmenge, team):
    tempname = 'Weitere ' + TblUserIDundName.objects \
        .filter(userid=userid).values('abteilung')[0]['abteilung']
    rolle = alte_oder_neue_restrolle(tempname, userid, team)

    erledigt = hole_soll_af_mengen(rollenmenge)
    rest = hole_alle_offenen_AFen_zur_userid(userid, erledigt)

    for eintrag in rest:
        if eintrag['enthalten_in_af'] == 'ka':
            continue
        af = TblAfliste.objects.filter(af_name=eintrag['enthalten_in_af'])
        if af.count() == 0:
            if TblAfliste.objects.filter(af_name='Noch_nicht_akzeptierte_AF').count() == 0:
                print('WARN: Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen')
                print('WARN: Auslöser ist', eintrag['enthalten_in_af'])
                af = TblUebersichtAfGfs.objects.create(
                    name_gf_neu='Noch_nicht_akzeptierte_GF',
                    name_af_neu='Noch_nicht_akzeptierte_AF',
                    kommentar='Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen',
                    zielperson='Alle',
                    af_text='Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen',
                    gf_text='',
                    af_langtext='',
                    af_ausschlussgruppen='',
                    af_einschlussgruppen='',
                    af_sonstige_vergabehinweise='',
                    geloescht=False,
                    kannweg=False,
                    modelliert=timezone.now(),
                )
                af.save()
                with connection.cursor() as cursor:
                    try:
                        cursor.callproc("erzeuge_af_liste")
                    except(e):
                        print('Fehler in alte_oder_neue_restrolle, StoredProc erzeuge_af_liste: {}'.format(e))
                    cursor.close()
            merkaf = TblAfliste.objects.get(af_name='Noch_nicht_akzeptierte_AF')
        else:
            merkaf = TblAfliste.objects.get(af_name=eintrag['enthalten_in_af'])

        neu = TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_NONE,
            bemerkung='Rechtebündel; Details siehe Konzept der Abteilung',
            af=merkaf,
            rollenname=rolle,
        )
        neu.save()
    return rolle


def alte_oder_neue_restrolle(tempname, userid, team):
    """
    Zunächst wird für den User gesucht, ob er bereits über eine "Weitere <Abteilungskürzel>"-Rolle verfügt.
    Falls ja, werden alle daran hängenden AF-Einträge in Tbl_RolleHatAF gelöscht
    :param tempname: Der ausgedachte Name der neuen oder alten Rolle
    :param userid:
    :param team: Die Referenz auf das Spezialteam. Wird benötigt zum Anlegen der UserHatRolle-Beziehung
    :return: Die alte und bereinigte oder die neu angelegte Rolle
    """

    weitereRolle = TblUserhatrolle.objects \
        .filter(userid__userid=userid) \
        .filter(rollenname=tempname)

    if weitereRolle.exists():
        afs_an_rolle = TblRollehataf.objects.filter(rollenname=tempname)
        afs_an_rolle.delete()

        # Ist die Teamspezfisch-Markierung schon mit der UserHatRolle-Eintrag verknüpft?
        uhr = TblUserhatrolle.objects.filter(
            userid=TblUserIDundName.objects.get(userid=userid),
            rollenname=tempname,
        )
        # ToDo: Sonderfall * in der Spezifikationslite in team.freies_team
        if uhr.count() > 0:
            # dann ist die Rolle bereits mit dem User verknüpft
            # Sicherheitshalber wird das Team-Spezifikum eingetragen, falls noch ein anderer Wert drin steht
            uhr = deepcopy(uhr[0])  # Sonst ist kein Update möglich - warum auch immer...
            if uhr.teamspezifisch != team:
                uhr.teamspezifisch = team
                uhr.save(force_update=True)
        else:  # Nein, muss noch verknüpft werden
            uhr = TblUserhatrolle.objects.create(
                userid=TblUserIDundName.objects.get(userid=userid),
                rollenname=tempname,
                schwerpunkt_vertretung='Schwerpunkt',
                bemerkung='Organisationsspezifische AFen',
                teamspezifisch=team,
                letzte_aenderung=timezone.now(),
            )
            uhr.save()
    else:
        # In diesem Fall gibt es die Rolle "Weitere <Abteilung>" noch gar nicht
        print('Rolle und Verknüpfung müssen komplett neu erstellt werden')
        rolle = TblRollen.objects.create(
            rollenname=tempname,
            system='Diverse',
            rollenbeschreibung='Organisationsspezifische AFen',
        )
        uhr = TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid=userid),
            rollenname=rolle,
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Organisationsspezifische AFen',
            teamspezifisch=team,
            letzte_aenderung=timezone.now(),
        )
        rolle.save()
        uhr.save()

    return TblRollen.objects.get(rollenname=tempname)


# Die beiden nachfolgenden Funktionen dienen nur dem Aufruf der eigentlichen Konzept-Funktion
def panel_UhR_konzept_pdf(request):
    return erzeuge_UhR_konzept(request, False)


def panel_UhR_konzept(request):
    return erzeuge_UhR_konzept(request, True)


# Fabric für das Behandeln von Rollenzuordnungen
class UhR(object):
    def factory(typ):
        if typ == 'einzel':
            return EinzelUhr()
        if typ == 'rolle':
            return RollenListenUhr()
        if typ == 'nur_neue':
            return NeueListenUhr()
        if typ == 'af':
            return AFListenUhr()
        assert 0, "Falsche Factory-Typ in Uhr: " + typ

    factory = staticmethod(factory)


# Ein einzelner User mit seiner UserID und all seinen vergebenen Rollen
class EinzelUhr(UhR):
    def setze_context(self, request, id):
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
        return context

    def behandle(self, request, id):
        return render(request, 'rapp/panel_UhR.html', self.setze_context(request, id))


# Für alle selektierten Used und ihre IDs alle AFen und die dazugehörigen Rollen
class RollenListenUhr(UhR):
    def setze_context(self, request):
        """
        Finde alle relevanten Informationen zur aktuellen Selektion
        Das ist die Factory-Klasse für die Betrachtung aller User mit spezifischen Rollen- oder AF-Namen

        :param request: GET oder POST Request vom Browser
        :param id: wird hier nicht verwendet, deshalb "_"
        :return: Zu renderndes HTML-File, Context für das zu rendernde HTML
        """
        (namen_liste, panel_filter, rollen_liste, rollen_filter) = \
            UhR_erzeuge_listen_mit_rollen(request)

        form = ShowUhRForm(request.GET)
        gesuchte_rolle = request.GET.get('rollenname', None)
        # Finde alle AFen in den verwendeten Rollen, die keinem der User zugewieen sind
        if gesuchte_rolle == "+":
            af_liste = hole_unnoetigte_afen(namen_liste)
            context = {
                'filter': panel_filter, 'form': form,
                'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
                'namen_liste': namen_liste,
                'af_liste': af_liste,
                'version': version,
            }
            return 'rapp/panel_UhR_ueberfluessige_af.html', context

        if gesuchte_rolle == "*":
            gesuchte_rolle = None

        (userids, af_per_uid, vorhanden, optional) = UhR_hole_rollengefilterte_daten(namen_liste, gesuchte_rolle)
        context = {
            'filter': panel_filter, 'form': form,
            'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
            'userids': userids,
            'af_per_uid': af_per_uid,
            'vorhanden': vorhanden,
            'optional': optional,
            'version': version,
        }
        return 'rapp/panel_UhR_rolle.html', context

    def behandle(self, request, _):
        html, cont = self.setze_context(request)
        return render(request, html, cont)


# Für alle selektierten User und deren IDs alle AFen, die für die konkrete UserID nicht zu Rollen zugeordnet sind
class NeueListenUhr(UhR):
    def setze_context(self, request):
        """
        Diese Factory-Klasse selektiert zunächst alle AFen,
        die für den jeweiligen User noch nicht mit einer Rolle belegt sind.

        Darüber hinaus werden alle Optionen gesucht, die für die jeweiligen AFen gültig sind.

        :param request: GET oder POST Request vom Browser
        :param id: wird hier nicht verwendet, deshalb "_"
        :return: Context für das zu rendernde HTML
        """
        (namen_liste, panel_filter, rollen_liste, rollen_filter) = \
            UhR_erzeuge_listen_mit_rollen(request)

        (userids, af_per_uid, vorhanden, optional) \
            = UhR_hole_rollengefilterte_daten(namen_liste, "-")

        form = ShowUhRForm(request.GET)
        context = {
            'filter': panel_filter, 'form': form,
            'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
            'userids': userids,
            'af_per_uid': af_per_uid,
            'vorhanden': vorhanden,
            'nur_neue': True,
            'optional': optional,
            'version': version,
        }
        return context

    def behandle(self, request, _):
        return render(request, 'rapp/panel_UhR_rolle.html', self.setze_context(request))


# For Future Use
class AFListenUhr(UhR):
    def behandle(self, request, id):
        assert 0, 'Funktion AFListenUhr::behandle() ist noch nicht implementiert. Der Aufruf ist nicht valide.'


# Zeige das Selektionspanel
def panel_UhR(request, id=0):
    """
    Finde die richtige Anzeige und evaluiere sie über das factory-Pattern

    - wenn rollenname = "-" ist, rufe die Factory "nur_neue"
    - wenn rollenname anderweitig gesetzt ist, rufe die Factory "rolle"
    - wenn rollenname nicht gesetzt oder leer ist und afname gesetzt ist, rufe factory "af"
    - Ansonsten rufe die Standard-Factory "einzel"

    :param request: GET oder POST Request vom Browser
    :param pk: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
    :return: Gerendertes HTML
    """
    assert request.method != 'POST', 'Irgendwas ist im panel_UhR über POST angekommen'
    assert request.method == 'GET', 'Irgendwas ist im panel_UhR nicht über GET angekommen: ' + request.method

    if request.GET.get('rollenname', None) is not None and request.GET.get('rollenname', None) == "-":
        name = 'nur_neue'
    elif request.GET.get('rollenname', None) is not None and request.GET.get('rollenname', None) != "":
        name = 'rolle'
    elif request.GET.get('afname', None) is not None and request.GET.get('afname', None) != "":
        print('Factory AF')
        name = 'af'
    else:
        name = 'einzel'

    obj = UhR.factory(name)
    return obj.behandle(request, id)


def erzeuge_pdf_namen(request):
    zeit = str(timezone.now())[:10]
    return 'Rollenkonzept_{}_{}.pdf'.format(zeit, request.GET.get('gruppe', ''))


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def erzeuge_datum():
    return str(timezone.now())[:10]


def erzeuge_ueberschrift(request):
    name = request.GET.get('name', '')
    teamnr = request.GET.get('orga', '')
    if representsInt(teamnr):
        team = TblOrga.objects.get(id=teamnr).team
    else:
        team = ''
    gruppe = request.GET.get('gruppe', '')
    if gruppe[-2:] == '--':  # Sonderzeichen für nicht-rekursive Auflösung von Organisationen
        gruppe = gruppe[:-2]

    retval = ''
    if name != '':
        retval = name
    if team != '':
        if retval != '':
            retval += ', Team '
        retval += team
    if gruppe != '':
        if retval != '':
            retval += ', '
        retval += gruppe
    return retval


def element_noch_nicht_vorhanden(liste, element):
    """
    Suche nach Einträgen in der übergebenen Menge,
    die - außer in der Klein-/Großschreibung - identisch mmit dem Suchstring sind

    :param menge: Die bereits vorhandene Menge
    :param element: Der Suchstring
    :return: True, wenn das Element noch nicht vorhanden ist, sonst False
    """
    suche = element.lower()
    for e in liste:
        if e['tf'].lower() == suche:
            return False
    return True


def liefere_racf_zu_tfs(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden RACF-Profile

    :param tf_menge: Die Menge der TFen, zu denen die RACF-Profile geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """
    suchmenge = set(t['tf'] for t in tf_menge)
    racf_liste = RACF_Rechte.objects \
        .filter(group__in=suchmenge) \
        .order_by('group', 'profil') \
        .values()
    return racf_liste


def liefere_db2_liste(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden Db2-Grantees

    :param tf_menge: Die Menge der TFen, zu denen die Db2-Grantee geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """
    suchmenge = set(t['tf'] for t in tf_menge)
    db2_liste = TblDb2.objects \
        .filter(grantee__in=suchmenge) \
        .order_by('grantee', 'source', 'table') \
        .values()
    return db2_liste


def liefere_win_lw_Liste(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden ACL-Einträge.
    Die ACL-Tabelle enthält nur den eigentlichen Namen im Active Directory.
    Die TF beschreibt jedoch den LDAP-Namen.
    Deshalb muss der eigentliche AD-Name aus den TFs extrahiert werden,
    bevor die DB-Abfrage erfolgen kann

    Da die ersten Zeichen in der AD-Notation nicht unbedingt mmit den TFen übereinstimmen,
    können wir erstnach mit dem ersten '_' beginnend vergleichen.
    Da es kein in-like gibt, muss die Suche zunächst manuell geschehen.

    Gleichzeitig wird die Liste der ACLs erstellt, für die keine Informationen gefunden wurden

    :param tf_menge: Die Menge der TFen, zu denen die Db2-Grantee geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """

    suchmenge = set()
    winacl = ACLGruppen.objects.order_by('tf', 'server', 'pfad').values()
    rest = set()

    for t in tf_menge:
        if 'CN=' in t['tf']:
            ad = re.search("^CN=\w+?(_[\w-]+?),", t['tf'])
            if ad == None:
                s = 'ACHTUNG: regexp konnte nicht mehr gefunden werden in Eintrag ' + t['tf']
                rest.add(s)
                continue
            for acl in winacl:
                if ad[1] in acl['tf']:
                    suchmenge.add(acl['tf'])
                    break;
            rest.add(t['tf'])

    retval = ACLGruppen.objects \
        .filter(tf__in=suchmenge) \
        .order_by('tf', 'server', 'pfad') \
        .distinct() \
        .values()

    return (retval, rest)


def kurze_tf_liste(aftf_dict):
    """
    Liefert zu einem AFTF_Dict die Menge der enthaltenen TFen

    Aus historischen Gründen erhalten wir dieselben TFen in verschiedenen
    Case-Schreibweisen.
    Beispiel:
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=gruppen,DC=RUV,DC=DE
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=Gruppen,DC=RUV,DC=DE
    Deshalb suchen wir zunächst nach dem einzufügenden Element in Klein-Schreibweise
    und fügen es nur dann dem Ergbnis hinzu, wenn es noch nicht existiert.

    :param af_menge: Ein Dictionary AF->TF, zu denen die TF-Menge geliefert werden soll
    :return: Die TF-Liste
    """

    tfInAF = list()
    for af in aftf_dict.values():
        for tf in af:
            if element_noch_nicht_vorhanden(tfInAF, tf['tf']):
                tfInAF.append(tf)
    return tfInAF


def liefere_tf_zu_afs(af_menge, userids):
    """
    Liefert zu einer AF-Liste die Menge der dazugehörenden TFen

    Aus historischen Gründen erhalten wir dieselben TFen in verschiedenen
    Case-Schreibweisen.
    Beispiel:
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=gruppen,DC=RUV,DC=DE
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=Gruppen,DC=RUV,DC=DE
    Deshalb suchen wir nach dem einzufügenden Element nur in Klein-Schreibweise
    und fügen es nur dann dem Ergbnis in Original-Schreibweise hinzu, wenn es noch nicht existiert.
    Damit wir die jeweils jüngste Schreibweise zurückliefern,
    erfolgt in der Query bereits eine Sortierung nach dem Datum des Auffindens.

    :param af_menge: Die Mmegne der AFen, zu denen die TF-Menge geliefert werden soll
    :param userids: Die Liste der Userids zum feineren Slektieren der Einträge in der Gesamttabelle
    :return: Menge der den Rollen zugeordneten TFen als Dict aftfDict[AF] => TF_Querysyset
    """

    tf_liste = TblGesamt.objects \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(geloescht=True) \
        .exclude(tf='Kein Name') \
        .exclude(tf='TF existiert nicht mehr') \
        .filter(enthalten_in_af__in=af_menge) \
        .filter(userid_name__userid__in=userids) \
        .order_by('-gefunden', '-wiedergefunden') \
        .values('enthalten_in_af',
                'af_beschreibung',
                'tf',
                'tf_beschreibung',
                'tf_kritikalitaet',
                'tf_eigentuemer_org',
                'plattform__tf_technische_plattform',
                'direct_connect',
                'hoechste_kritikalitaet_tf_in_af'
                )

    retvalDict = {}
    afset = set([af['enthalten_in_af'] for af in tf_liste])
    for af in afset:
        tfInAF = list()

        for tf in tf_liste:
            # Betrachte nur die TFe für die aktuelle AF
            if tf['enthalten_in_af'] != af:
                continue
            # leider ist tf nicht "set-fähig"
            if element_noch_nicht_vorhanden(tfInAF, tf['tf']):
                tfInAF.append(tf)
        retvalDict[af] = tfInAF
        # print('ratvalDict = {}'.format(retvalDict))
    return retvalDict


def liefere_tf_liste(rollenMenge, userids):
    """
    Liefet zu einer Menge an Rollen die zugehörenden TFen.
    Dies geschieht zunächst über die Ermittlung der Arbeitsplatzfunktionen,
    die für die angegebenen Rollen definiert sind.
    In der Anzeige müssen die jeweiligen TFs zu ihren AFs dargestellt werden können,
    das ist besonders bei redundant mmodellierten TFen relevant.
    :param rollenMenge:
    :return: Menge der den Rollen zugeordneten TFen als Dict aftfDict[AF] = TF_Querysyset
    """
    af_menge = liefere_af_menge(rollenMenge)
    aftf_dict = liefere_tf_zu_afs(af_menge, userids)
    return aftf_dict


def liefere_af_menge(rollenMenge):
    """
    Liefert die Menge der AFen, die von einer Menge an Rollen adressiert wird
    :param rollenMenge: Die Menge an Rollen, zu denen die AFen gesucht werden
    :return: af_menge aller gefundener AFen
    """
    af_menge = set()
    for rolle in rollenMenge:
        af_liste = liefere_af_zu_rolle(rolle)
        af_menge.update(set([af['af__af_name'] for af in af_liste]))
    return af_menge


def liefere_af_kritikalitaet(rollenMenge, userids):
    """
    Für die Menge der gegebenen Rollen liefer die Liste der jeweils höchsten TF-Kritikalitäten.
    Achtung: Bei veralteten Daten in der Gesamt-Tabelle kann es sein, dass diese Informationen
    ebenfalls nicht mehr korrekt sind. Deshalb erfolgt eine Filterung nach UserIDen,
    um ausschließlich aktuelle Werte in der Gesamt-Tabelle zu selektieren.

    :param rollenMenge: Hierüber wird die LIste der AFen ermmittelt, die adressiert werden sollen
    :param userids: Dies dient der Reduzierung der Treffermenge (nur die gefundenen AF/TF-Kombination zu den UserIDs)
    :return: Das Dict der AF => Höchste_Kritikalität_der_TF_in_der_AF laut dem IIQ-Feld
    """
    # .filter(userid_name__userid__in=userids) \

    af_menge = liefere_af_menge(rollenMenge)
    krit_liste = TblGesamt.objects \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(geloescht=True) \
        .exclude(tf='Kein Name') \
        .filter(enthalten_in_af__in=af_menge) \
        .order_by('enthalten_in_af', '-letzte_aenderung') \
        .values('enthalten_in_af',
                'hoechste_kritikalitaet_tf_in_af',
                'letzte_aenderung',
                )

    # Merke den jeweils jüngsten Eintrag je AF, ignoriere Case
    hoechste_kritikalitaet_tf_in_af = {}
    letzter_eintrag = ''
    for krit in krit_liste:
        """
        print(krit['enthalten_in_af'], ' ->', krit['hoechste_kritikalitaet_tf_in_af'],
            'letzte_aenderung =', krit['letzte_aenderung'],
            'Letzter Eintrag war', letzter_eintrag
        )
        """
        if krit['enthalten_in_af'].lower() != letzter_eintrag:
            hoechste_kritikalitaet_tf_in_af[krit['enthalten_in_af']] \
                = str(krit['hoechste_kritikalitaet_tf_in_af']).lower()
            letzter_eintrag = str(krit['enthalten_in_af']).lower()
    return hoechste_kritikalitaet_tf_in_af


# Erzeuge das Berechtigungskonzept für Anzeige und PDF
def erzeuge_UhR_konzept(request, ansicht):
    """
    Erzeuge das Berechtigungskonzept für eine Menge an selektierten Identitäten.

    :param request: GET Request vom Browser
    :param ansicht: Flag, ob die Daten als HTML zur Ansicht oder als PDF zum Download geliefert werden sollen
    :return: Gerendertes HTML
    """

    def log(request, rollenMenge, userids, usernamen):
        if request.GET.get('display') == '1':
            print('rollenMenge')
            print(rollenMenge)

            print('userids')
            for a in userids:
                print(a)

            print('usernamen')
            for a in usernamen:
                print(a)

    # Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
    (namen_liste, panel_filter) = UhR_erzeuge_gefiltere_namensliste(request)

    if request.method == 'GET':
        (rollenMenge, userids, usernamen) = UhR_verdichte_daten(request, namen_liste)
    else:
        (rollenMenge, userids, usernamen) = (set(), set(), set())

    log(request, rollenMenge, userids, usernamen)

    af_kritikalitaet = liefere_af_kritikalitaet(rollenMenge, userids)

    winnoe = None
    tf_liste = None
    aftf_dict = None
    db2_liste = None
    racf_liste = None
    winacl_Liste = None

    # episch = 0: Liefere nur das generierte Konzept
    # episch = 1: Liefere zusätzlich die TF-Liste
    # episch = 9: Liefere alles, was in der DB zu finden ist
    episch = int(request.GET.get('episch', 0))
    if episch >= 1:
        aftf_dict = liefere_tf_liste(rollenMenge, userids)
        tf_liste = kurze_tf_liste(aftf_dict)

    if episch == 9:
        racf_liste = liefere_racf_zu_tfs(tf_liste)
        db2_liste = liefere_db2_liste(tf_liste)
        (winacl_Liste, winnoe) = liefere_win_lw_Liste(tf_liste)

    context = {
        'filter': panel_filter,
        'rollenMenge': rollenMenge,
        'aftf_dict': aftf_dict,
        'af_kritikalitaet': af_kritikalitaet,
        'racf_liste': racf_liste,
        'db2_liste': db2_liste,
        'winacl_liste': winacl_Liste,
        'winnoe': winnoe,
        'version': version,
        'ueberschrift': erzeuge_ueberschrift(request),
        'episch': episch,
    }
    if (ansicht):
        return render(request, 'rapp/panel_UhR_konzept.html', context)

    pdf = render_to_pdf('rapp/panel_UhR_konzept_pdf.html', context)
    if pdf:
        return erzeuge_pdf_header(request, pdf)
    return HttpResponse("Fehlerhafte PDF-Generierung in erzeuge_UhR_konzept")


def erzeuge_pdf_header(request, pdf):
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = erzeuge_pdf_namen(request)
    content = "inline; filename={}".format(filename)
    download = request.GET.get("download")
    if download:
        content = "attachment; filename={}".format(filename)
    response['Content-Disposition'] = content
    return response


# Funktionen zum Erstellen des Funktionsmatrix
def erzeuge_UhR_matrixdaten(request, panel_liste):
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

    :param request: für die Fallunterscheidung spezifisches_team
    :param panel_liste: Die Menge der betrachteten User
    :return: usernamen, rollenmenge als Liste, rollen_je_username, teams_je_username
    """
    usernamen = set()  # Die Namen aller User,  die in der Selektion erfasst werden
    rollenmenge = set()  # Die Menge aller AFs aller spezifizierten User (aus Auswahl-Panel)
    teams_je_username = {}  # Derzeit nur ein Team/UserID, aber multi-Teams müssen vorbereitet werden
    rollen_je_username = {}  # Die Rollen, die zum Namen gehören

    for row in panel_liste:
        usernamen.add(row.name)
        teamliste = TblOrga.objects \
            .filter(tbluseridundname__name=row.name, tbluseridundname__geloescht=False) \
            .exclude(team="Gelöschter User")  # Die als gelöscht markierten User werden nicht mehr angezeigt

        teammenge = set()
        for team in teamliste:
            teammenge.add(str(team))
        teams_je_username[row.name] = [str(team) for team in teammenge]

        # Erzeuge zunächst die Hashes für die UserIDs. Daran werden nachher die Listen der Rechte gehängt.
        rollen_je_username[row.name] = set()

        # Fallunterscheidung nach "freies_team" und "spezielles_team"
        if kein_freies_team(request) or soll_komplett(request, row):  # Standardfall
            rollen = TblUserhatrolle.objects.filter(userid=row.userid)
        else:
            spezialteam = TblOrga.objects.get(id=request.GET.get('orga'))
            print('\nspezial_team =', spezialteam)
            print('erzeuge_UhR_matrixdaten für Userid {}, {}'.format(row.userid, row.name))
            rollen = TblUserhatrolle.objects \
                .filter(userid=row.userid) \
                .filter(teamspezifisch=spezialteam)

        # Merke die Rollen je Usernamen (also global für alle UserIDs der Identität)
        # sowie die Menge aller gefundenen Rollennamen
        # Achtung: rolle ist nur eine für den User spezifische Linknummer auf das Rollenobjekt.
        for rolle in rollen:
            info = (rolle.rollenname, rolle.schwerpunkt_vertretung)
            rollen_je_username[row.name].add(info)
            rollenmenge.add(rolle.rollenname)

    def order(a):
        return a.rollenname.lower()  # Liefert das kleingeschriebene Element, nach dem sortiert werden soll

    return (sorted(usernamen), sorted(list(rollenmenge), key=order), rollen_je_username, teams_je_username)


def panel_UhR_matrix(request):
    """
    Erzeuge eine Verantwortungsmatrix für eine Menge an selektierten Identitäten.
    :param request: GET Request vom Browser
    :return: Gerendertes HTML
    """

    def logging(request, rollen_je_username, rollenmenge, usernamen):
        if request.GET.get('display') == '1':
            print('usernamen')
            print(usernamen)

            print('rollenmenge')
            for a in rollenmenge:
                print(a)

            print('rollen_je_username')
            for a in rollen_je_username:
                print(a, rollen_je_username[a])

    # Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
    (namen_liste, panel_filter) = UhR_erzeuge_gefiltere_namensliste(request)

    if request.method == 'GET':
        (usernamen, rollenmenge, rollen_je_username, teams_je_username) = erzeuge_UhR_matrixdaten(request, namen_liste)
    else:
        (usernamen, rollenmenge, rollen_je_username, teams_je_username) = (set(), set(), set(), {})

    logging(request, rollen_je_username, rollenmenge, usernamen)
    context = {
        'filter': panel_filter,
        'usernamen': usernamen,
        'rollenmenge': rollenmenge,
        'rollen_je_username': rollen_je_username,
        'teams_je_username': teams_je_username,
        'version': version,
    }
    return render(request, 'rapp/panel_UhR_matrix.html', context)


def string_aus_liste(liste):
    """
    Erzeugt einen String, der alle Listenelemente der Parameters Kommma-getrennt enthält
    :param liste: Eine Liste mit Strings, bspw. ['abc', 'def']
    :return: String mit den Inhalten, getrennt durch ', ': "abc, def"
    """
    res = ""
    for s in liste:
        if (res == ""):
            res = s
        else:
            res += (", " + s)
    return res


def panel_UhR_matrix_csv(request, flag=False):
    """
    Exportfunktion für das Filter-Panel zum Selektieren aus der "User und Rollen"-Tabelle).
    :param request: GET oder POST Request vom Browser
    :param flag: False oder nicht gegeben -> liefere ausführliche Text, 'kommpakt' -> liefere nur Anfangsbuchstaben
    :return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
    """
    if request.method != 'GET':
        return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_matrix_csv")

    (namen_liste, _) = UhR_erzeuge_gefiltere_namensliste(request)
    (usernamen, rollenmenge, rollen_je_username, teams_je_username) = erzeuge_UhR_matrixdaten(request, namen_liste)

    headline = [smart_str(u'Name')] + [smart_str(u'Teams')]
    for r in rollenmenge:
        headline += [smart_str(r.rollenname)]

    excel = Excel("matrix.csv")
    excel.writerow(headline)

    for user in usernamen:
        line = [user] + [smart_str(string_aus_liste(teams_je_username[user]))]
        for rolle in rollenmenge:
            if flag:
                wert = finde(rollen_je_username[user], rolle)
                if wert == None or len(wert) <= 0:
                    line += ['']
                else:
                    line += [smart_str(wert[0])]
            else:
                line += [smart_str(finde(rollen_je_username[user], rolle))]
        excel.writerow(line)

    return excel.response


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

    headline = [
        smart_str(u'Name'),
        smart_str(u'Rollenname'),
        smart_str(u'AF'),
        smart_str(u'Mussrecht')
    ]
    for userid in selektierte_userids:
        headline.append(smart_str(userid))

    excel = Excel("rollen.csv")
    excel.writerow(headline)

    for rolle in userHatRolle_liste:
        for rollendefinition in TblRollehataf.objects.filter(rollenname=rolle.rollenname):
            line = [selektierter_name, rolle.rollenname, rollendefinition.af]
            if rollendefinition.mussfeld > 0:
                line.append('ja')
            else:
                line.append('nein')
            for userid in selektierte_userids:
                if str(rollendefinition.af).strip().lower() in afmenge_je_userID[userid]:
                    line.append('ja')
                else:
                    line.append('nein')
            excel.writerow(line)

    return excel.response
