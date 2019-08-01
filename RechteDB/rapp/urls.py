"""books URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import 	views, view_UserHatRolle, view_import, stored_procedures, view_serienbrief, \
				view_neueAFGF
from django.contrib.auth.decorators import login_required


# app_name = 'rapp'		# Wird nur benötigt als namespace, falls mehrere Apps dieselbe Teil-URL haben

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

# Der Link auf die Team-liste
urlpatterns += [
	path('teamliste/', login_required(views.TeamListView.as_view()), name='teamliste'),
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
	path('user_rolle_af/<int:pk>/delete/', 		login_required(view_UserHatRolle.UhRDelete.as_view()), 		name='user_rolle_af-delete'),
	path('user_rolle_af/<str:userid>/create/<str:rollenname>/<str:schwerpunkt_vertretung>',
		 										login_required(view_UserHatRolle.UhRCreate.as_view()), 		name='uhr_create'),
	path('user_rolle_af/<int:id>/', 			login_required(view_UserHatRolle.panel_UhR), 				name='user_rolle_af_parm'),
	path('user_rolle_af/export/<int:id>/',		login_required(view_UserHatRolle.panel_UhR_af_export), 		name='user_rolle_af_export'),
	path('user_rolle_af/create/<str:userid>/',	login_required(view_UserHatRolle.UhRCreate.as_view()), 		name='user_rolle_af-create' ),
	path('user_rolle_af/konzept/', 				login_required(view_UserHatRolle.panel_UhR_konzept),		name='uhr_konzept'),
	path('user_rolle_af/konzept_pdf/', 			login_required(view_UserHatRolle.panel_UhR_konzept_pdf), 	name='uhr_konzept_pdf'),
	path('user_rolle_af/matrix/', 				login_required(view_UserHatRolle.panel_UhR_matrix), 		name='uhr_matrix'),
	path('user_rolle_af/matrix_csv/', 			login_required(view_UserHatRolle.panel_UhR_matrix_csv), 	name='uhr_matrix_csv'),
	path('user_rolle_af/matrix_csv/<str:flag>/',
		 										login_required(view_UserHatRolle.panel_UhR_matrix_csv), 	name='uhr_matrix_csv'),
	path('user_rolle_af/', 						login_required(view_UserHatRolle.panel_UhR), 				name='user_rolle_af'),
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

# Finden neuer Kombiunationen aus AF und GF: Anzeige und spezifische Aktualisierung
urlpatterns += [
	path('neue_afgf/', login_required(view_neueAFGF.zeige_neue_afgf), name='zeige_neue_afgf'),
	path('neueAFGF_download/', login_required(view_neueAFGF.neue_afgf_download), name='neueAFGF_download'),
	path('neueAFGF_setzen/', login_required(view_neueAFGF.neueAFGF_setzen), name='neueAFGF_setzen'),
]

# URl zum Testen neuer Funktionalität (liegt in "Magie")
urlpatterns += [
	path('magic_click/', login_required(views.magic_click), name='magic_click'),
]
