from django.contrib.auth.models import User, Group
from .models import TblGesamt, TblUserIDundName, TblUserhatrolle

import django_filters
from django import forms


class PanelFilter(django_filters.FilterSet):
	tf = 							django_filters.CharFilter(lookup_expr='icontains')
	enthalten_in_af = 				django_filters.CharFilter(lookup_expr='icontains')
	userid_name__name = 			django_filters.CharFilter(lookup_expr='istartswith')
	userid_name__userid = 			django_filters.CharFilter(lookup_expr='istartswith')
	geloescht = 					django_filters.BooleanFilter()
	userid_name__geloescht = 		django_filters.BooleanFilter()

	userid_name__zi_organisation = 	django_filters.CharFilter(lookup_expr='icontains')
	modell__name_af_neu = 			django_filters.CharFilter(lookup_expr='icontains')
	modell__name_gf_neu = 			django_filters.CharFilter(lookup_expr='icontains')

	plattform_id__tf_technische_plattform =\
									django_filters.ChoiceFilter()


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
			'userid_name__geloescht', \
			'userid_name__zi_organisation', \
			'modell__name_af_neu', \
			'modell__name_gf_neu', \
			]
