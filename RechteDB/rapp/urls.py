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
from . import views, view_UserHatRolle, view_import, stored_procedures

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
	path('gesamtliste/', views.GesamtListView.as_view(), name='gesamtliste'),
]

# Der Link auf ein einzelnes Recht aus der Gesamtliste mit seiner generierten Detailsicht
urlpatterns += [
	path('gesamtliste/<int:pk>', views.GesamtDetailView.as_view(), name='gesamt-detail'),
]

# Der Link auf die User-liste
urlpatterns += [
	path('userliste/', views.UserIDundNameListView.as_view(), name='userliste'),
]

# Generische Formulare für CUD UserIDundName (werden im Frontend bedient)
urlpatterns += [
	path('user/<int:pk>/delete/', views.TblUserIDundNameDelete.as_view(), name='user-delete'),
	path('user/create/', views.TblUserIDundNameCreate.as_view(), name='user-create'),
	path('user/<int:pk>/update/', views.TblUserIDundNameUpdate.as_view(), name='user-update'),
	path('user/<int:pk>/toggle_geloescht/', views.userToggleGeloescht, name='user-toggle-geloescht'),
]

# Der Link auf die Team-liste
urlpatterns += [
	path('teamliste/', views.TeamListView.as_view(), name='teamliste'),
]

# Generische Formulare für CUD Orga (Teams, werden im Frontend bedient)
urlpatterns += [
	path('team/<int:pk>/delete/', views.TblOrgaDelete.as_view(), name='team-delete'),
	path('team/create/', views.TblOrgaCreate.as_view(), name='team-create'),
	path('team/<int:pk>/update/', views.TblOrgaUpdate.as_view(), name='team-update'),
]

# Der Link auf das Eingabepanel zur freien Selektion direkt auf der Gesamttabelle
urlpatterns += [
	path('panel/download', views.panelDownload, name='panel_download'),
	path('panel/', views.panel, name='panel'),
]

# Der Link auf das Eingabepanel zur freien Selektion auf der User-hat-Rolle Tabelle mit Änderungslink
urlpatterns += [
	path('user_rolle_af/<int:pk>/delete/', 		view_UserHatRolle.UhRDelete.as_view(), 		name='user_rolle_af-delete'),
	# path('user_rolle_af/<int:pk>/update/', 		view_UserHatRolle.UhRUpdate.as_view(), 		name='user_rolle_af-update'),
	path('user_rolle_af/<int:id>/', 			view_UserHatRolle.panel_UhR, 				name='user_rolle_af_parm'),
	path('user_rolle_af/create/<str:userid>/',	view_UserHatRolle.UhRCreate.as_view(), 		name='user_rolle_af-create' ),
	path('user_rolle_af/konzept/', 				view_UserHatRolle.panel_UhR_konzept,		name='uhr_konzept'),
	path('user_rolle_af/konzept_pdf/', 			view_UserHatRolle.panel_UhR_konzept_pdf, 	name='uhr_konzept_pdf'),
	path('user_rolle_af/matrix/', 				view_UserHatRolle.panel_UhR_matrix, 		name='uhr_matrix'),
	path('user_rolle_af/matrix_csv/', 			view_UserHatRolle.panel_UhR_matrix_csv, 	name='uhr_matrix_csv'),
	path('user_rolle_af/matrix_csv/<str:flag>/',
		 										view_UserHatRolle.panel_UhR_matrix_csv, 	name='uhr_matrix_csv'),
	path('user_rolle_af/', 						view_UserHatRolle.panel_UhR, 				name='user_rolle_af'),
]

# URl zum Importieren neuer Daten aus IIQ (csv-File)
urlpatterns += [
	path('import/', view_import.import_csv, name='import'),
	path('import2/', view_import.import2, name='import2'),
	path('import2_quittung/', view_import.import2_quittung, name='import2_quittung'),
	path('import3_quittung/', view_import.import3_quittung, name='import3_quittung'),
	path('import_reset/', view_import.import_reset, name='import_reset'),
	path('import_status/', view_import.import_status, name='import_status'),
]

# URl zum Bestücken der verschiedenen Stored Procedures in das DBMS
urlpatterns += [
	path('stored_procedures/', stored_procedures.handle_stored_procedures, name='stored_procedures'),
]

# URl zum Testen neuer Funktionalität (liegt in "Magie")
urlpatterns += [
	path('magic_click/', views.magic_click, name='magic_click'),
]

