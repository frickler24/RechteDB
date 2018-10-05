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
from . import views
from django.conf.urls import url
from django_filters.views import FilterView
#from .filters import UserFilter

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
	path('panel/', views.panel, name='panel'),
]

# Der Link auf das Eingabepanel zur freien Selektion auf der Usertabelle mit Änderungslink
urlpatterns += [
	path('user_rolle_af/<int:pk>/delete/', views.UhRDelete.as_view(), name='user_rolle_af-delete'),
	path('user_rolle_af/<int:id>/', views.panel_UhR, name='user_rolle_af_parm'),
	path('user_rolle_af/create/<str:userid>/', views.UhRCreate.as_view(), name='user_rolle_af-create' ),
	path('user_rolle_af/create/', views.UhRCreate.as_view(), name='user_rolle_af-create' ),
	path('user_rolle_af/', views.panel_UhR, name='user_rolle_af'),
]

# URl zum Importieren neuer Daten aus IIQ (csv-File)
urlpatterns += [
	path('import/', views.import_csv, name='import'),
]

# URl zum Bestücken der verschiedenen Stored Procedures in das DBMS
urlpatterns += [
	path('stored_procedures/', views.handle_stored_procedures, name='stored_procedures'),
]

