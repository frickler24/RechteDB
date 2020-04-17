from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from . import view_UserHatRolle
from . import view_import
from . import stored_procedures
from . import view_serienbrief
from . import view_neueAFGF
from . import view_manuell
from . import view_rolle_umbenennen
from . import view_ungenutzte_rollen
from . import view_ungenutzte_afgf

# app_name = 'rapp'        # Wird nur benötigt als namespace, falls mehrere Apps dieselbe Teil-URL haben

# Der Index als zentraler Einstieg
urlpatterns = [
    # klassenbasierter Aufruf
    # path('', views.IndexView.as_view(), name='index'),

    # Funktionsorientierte Form des Aufrufs
    path('', views.home, name='home'),
]

# Der Link auf die Gesamtliste
urlpatterns += [
    path('gesamtliste/', login_required(views.GesamtListView.as_view()), name='gesamtliste'),
]

# Der Link auf ein einzelnes Recht aus der Gesamtliste mit seiner generierten Detailsicht
urlpatterns += [
    path('gesamtliste/<int:pk>', login_required(views.GesamtDetailView.as_view()), name='gesamt-detail'),
]

# Der Link auf die User-liste
urlpatterns += [
    path('userliste/', login_required(views.UserIDundNameListView.as_view()), name='userliste'),
]

# Generische Formulare für CUD UserIDundName (werden im Frontend bedient)
urlpatterns += [
    path('user/<int:pk>/delete/', login_required(views.TblUserIDundNameDelete.as_view()), name='user-delete'),
    path('user/create/', login_required(views.TblUserIDundNameCreate.as_view()), name='user-create'),
    path('user/<int:pk>/update/', login_required(views.TblUserIDundNameUpdate.as_view()), name='user-update'),
    path('user/<int:pk>/toggle_geloescht/', login_required(views.userToggleGeloescht), name='user-toggle-geloescht'),
]

# Der Link auf die Team-Listen
urlpatterns += [
    path('teamliste/', login_required(views.TeamListView.as_view()), name='teamliste'),
    path('ungenutzteTeams/', login_required(views.panel_ungenutzteTeams), name='ungenutzteTeams'),
]

# Generische Formulare für CUD Orga (Teams, werden im Frontend bedient)
urlpatterns += [
    path('team/<int:pk>/delete/', login_required(views.TblOrgaDelete.as_view()), name='team-delete'),
    path('team/create/', login_required(views.TblOrgaCreate.as_view()), name='team-create'),
    path('team/<int:pk>/update/', login_required(views.TblOrgaUpdate.as_view()), name='team-update'),
]

# Der Link auf das Eingabepanel zur freien Selektion direkt auf der Gesamttabelle
urlpatterns += [
    path('panel/download', login_required(views.panelDownload), name='panel_download'),
    path('panel/', login_required(views.panel), name='panel'),
]

# Der Link auf das Eingabepanel zur freien Selektion auf der User-hat-Rolle Tabelle (UhR)
urlpatterns += [
    path('user_rolle_af/<int:pk>/delete/',
        login_required(view_UserHatRolle.UhRDelete.as_view()),
        name='user_rolle_af-delete'),
    path('user_rolle_af/<str:userid>/create/<str:rollenname>/<str:schwerpunkt_vertretung>',
        login_required(view_UserHatRolle.UhRCreate.as_view()),
        name='uhr_create'),
    path('user_rolle_af/<int:id>/',
         login_required(view_UserHatRolle.panel_UhR),
         name='user_rolle_af_parm'),
    path('user_rolle_af/export/<int:id>/',
         login_required(view_UserHatRolle.panel_UhR_af_export),
         name='user_rolle_af_export'),
    path('user_rolle_af/create/<str:userid>/',
         login_required(view_UserHatRolle.UhRCreate.as_view()),
         name='user_rolle_af-create' ),
    path('user_rolle_af/konzept/',
         login_required(view_UserHatRolle.panel_UhR_konzept),
         name='uhr_konzept'),
    path('user_rolle_af/konzept_pdf/',
         login_required(view_UserHatRolle.panel_UhR_konzept_pdf),
         name='uhr_konzept_pdf'),
    path('user_rolle_af/matrix/',
         login_required(view_UserHatRolle.panel_UhR_matrix),
         name='uhr_matrix'),
    path('user_rolle_af/matrix_csv/',
         login_required(view_UserHatRolle.panel_UhR_matrix_csv),
         name='uhr_matrix_csv'),
    path('user_rolle_af/matrix_csv/<str:flag>/',
         login_required(view_UserHatRolle.panel_UhR_matrix_csv),
         name='uhr_matrix_csv'),
    path('user_rolle_af/',
         login_required(view_UserHatRolle.panel_UhR),
         name='user_rolle_af'),
]

# Die Behandlujng der Beschreibungen manuell zu verwaltender Berechtigungen
# Hier sollte auch der mdeditor mitspielen
urlpatterns += [
    path('manuell/<int:pk>/delete/',
         login_required(view_manuell.Manuelle_BerechtigungDelete.as_view()), name='manuell_delete'),
    path('manuell/<int:pk>/update/',
         login_required(view_manuell.Manuelle_BerechtigungUpdate.as_view()), name='manuell_update'),
    path('manuell/create/',
         login_required(view_manuell.ManuelleBerechtigungCreate.as_view()), name='manuell_create'),
    path('manuell/',
         login_required(view_manuell.Manuelle_BerechtigungListe.as_view()), name='manuell_liste'),
]

# URl zum Importieren neuer Daten aus IIQ (csv-File)
urlpatterns += [
    path('import/', login_required(view_import.import_csv), name='import'),
    path('import2/', login_required(view_import.import2), name='import2'),
    path('import2_quittung/', login_required(view_import.import2_quittung), name='import2_quittung'),
    path('import3_quittung/', login_required(view_import.import3_quittung), name='import3_quittung'),
    path('import_reset/', login_required(view_import.import_reset), name='import_reset'),
    path('import_status/', login_required(view_import.import_status), name='import_status'),
]

# URl zum Bestücken der verschiedenen Stored Procedures in das DBMS
urlpatterns += [
    path('stored_procedures/', login_required(stored_procedures.handle_stored_procedures), name='stored_procedures'),
]

# URl zum Erzeugen der LaTeX-Serienbriefinformation zu Direct Connects
urlpatterns += [
    path('einzelbrief/', login_required(view_serienbrief.einzelbrief), name='einzelbrief'),
    path('serienbrief/', login_required(view_serienbrief.serienbrief), name='serienbrief'),
]

# Finden neuer Kombinationen aus AF und GF: Anzeige und spezifische Aktualisierung
urlpatterns += [
    path('neue_afgf/', login_required(view_neueAFGF.zeige_neue_afgf), name='zeige_neue_afgf'),
    path('neueAFGF_download/', login_required(view_neueAFGF.neue_afgf_download), name='neueAFGF_download'),
    path('neueAFGF_setzen/', login_required(view_neueAFGF.neueAFGF_setzen), name='neueAFGF_setzen'),
]

# Finden ungenutzter Kombinationen aus AF und GF: Anzeige mit spezifischen Links auf die jeweilige Adminseite
urlpatterns += [
    path('ungenutzte_afgf/', login_required(view_ungenutzte_afgf.panel_ungenutzte_afgf), name='ungenutzte_afgf'),
]

# Kopieren und Namensänderungen von Rollen
urlpatterns += [
    path('rolle_umbenennen/', login_required(view_rolle_umbenennen.panel_rolle_umbenennen), name='rolle_umbenennen'),
    path('ungenutzte_rollen/', login_required(view_ungenutzte_rollen.panel_ungenutzte_rollen), name='ungenutzte_rollen'),
    # ToDo: path('rolle_kopieren/', login_required(views.panel_rolle_kopieren), name='rolle_kopieren'),
]

# URl zum Testen neuer Funktionalität (liegt in "Magie")
urlpatterns += [
    path('magic_click/', login_required(views.magic_click), name='magic_click'),
]
