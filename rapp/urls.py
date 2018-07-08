from django.urls import path

from . import views

app_name = 'rapp'		# Wird nur benötigt als namespace, falls mehrere Apps dieselbe Teil-URL haben

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'),
]

"""
path('<int:pk>/', views.DetailView.as_view(), name='detail'),
path('<int:pk>/', views.DetailView.as_view(), name='detail'),
path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
path('<int:question_id>/vote/', views.vote, name='vote'),

"""
