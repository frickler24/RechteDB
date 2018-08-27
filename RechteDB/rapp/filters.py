from django.contrib.auth.models import User, Group
from .models import TblGesamt, TblUserIDundName

import django_filters
from django import forms

"""
class UserFilter(django_filters.FilterSet):
	# first_name = django_filters.CharFilter(lookup_expr='icontains')
	# year_joined = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year')
	class Meta:
		model = User
		fields = {
			'username': ['exact', ],
			'first_name': ['icontains', ],
			'last_name': ['exact', ],
			'date_joined': ['year', 'year__gt', 'year__lt', ],
		}
		# fields = ['username', 'first_name', 'last_name', ]

"""

class UserFilter(django_filters.FilterSet):
	first_name = django_filters.CharFilter(lookup_expr='icontains')
	year_joined = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year')
	groups = django_filters.ModelMultipleChoiceFilter(queryset=Group.objects.all(),
													  widget=forms.CheckboxSelectMultiple)
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'year_joined', 'groups']


class UserIDFilter(django_filters.FilterSet):
	userid = django_filters.CharFilter(lookup_expr='istartswith')
	name = django_filters.CharFilter(lookup_expr='icontains')
	geloescht = django_filters.BooleanFilter(lookup_expr='exact')

	class Meta:
		model = TblUserIDundName
		fields = '__all__'



class PanelFilter(django_filters.FilterSet):
	tf = 							django_filters.CharFilter(lookup_expr='icontains')
	enthalten_in_af = 				django_filters.CharFilter(lookup_expr='icontains')
	userid_name__name = 			django_filters.CharFilter(lookup_expr='istartswith')
	userid_name__userid = 			django_filters.CharFilter(lookup_expr='istartswith')
	geloescht = 					django_filters.BooleanFilter(initial = False)

	userid_name__zi_organisation = 	django_filters.CharFilter(lookup_expr='icontains')
	modell__name_af_neu = 			django_filters.CharFilter(lookup_expr='icontains')
	modell__name_gf_neu = 			django_filters.CharFilter(lookup_expr='icontains')

	# plattform = 					django_filters.ChoiceFilter()	# DoDo: Reparieren gelöscht Anzeige


	class Meta:
		model = TblGesamt
		fields = [
			'id', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'modell', 'tf_kritikalitaet', \
			'tf_eigentuemer_org', 'plattform', 'gf', 'af_gueltig_ab', 'af_gueltig_bis', 'direct_connect', \
			'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung', 'af_zuweisungsdatum', 'datum', \
			'geloescht', 'loeschdatum', \
			'userid_name__orga', \
			'userid_name__name', \
			'userid_name__userid', \
			'userid_name__zi_organisation', \
			'modell__name_af_neu', \
			'modell__name_gf_neu', \
			]

