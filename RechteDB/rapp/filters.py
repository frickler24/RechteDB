from .models import TblGesamt, TblUserIDundName, TblUserhatrolle, TblRollehataf
import django_filters

class PanelFilter(django_filters.FilterSet):
	tf = 							django_filters.CharFilter(lookup_expr='icontains')
	tf_beschreibung =				django_filters.CharFilter(lookup_expr='icontains')
	enthalten_in_af = 				django_filters.CharFilter(lookup_expr='icontains')
	userid_name__name = 			django_filters.CharFilter(lookup_expr='istartswith')
	userid_name__userid = 			django_filters.CharFilter(lookup_expr='istartswith')
	geloescht = 					django_filters.BooleanFilter()
	userid_name__geloescht = 		django_filters.BooleanFilter()
	userid_name__gruppe = 			django_filters.CharFilter(lookup_expr='icontains')
	userid_name__zi_organisation = 	django_filters.CharFilter(lookup_expr='icontains')
	modell__name_af_neu = 			django_filters.CharFilter(lookup_expr='icontains')
	modell__name_gf_neu = 			django_filters.CharFilter(lookup_expr='icontains')

	plattform_id__tf_technische_plattform =\
									django_filters.ChoiceFilter()

	class Meta:
		model = TblGesamt
		fields = [
			'id', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'modell', 'tf_kritikalitaet',
			'tf_eigentuemer_org', 'plattform', 'gf', 'af_gueltig_ab', 'af_gueltig_bis', 'direct_connect',
			'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung', 'af_zuweisungsdatum', 'datum',
			'geloescht', 'loeschdatum',
			'userid_name__orga',
			'userid_name__name',
			'userid_name__userid',
			'userid_name__geloescht',
			'userid_name__zi_organisation',
			'userid_name__gruppe',
			'modell__name_af_neu',
			'modell__name_gf_neu',
		]

class UseridRollenFilter(django_filters.FilterSet):
	userid__name = 				django_filters.CharFilter(lookup_expr='istartswith')
	userid__userid = 			django_filters.CharFilter(lookup_expr='istartswith')
	userid__geloescht = 		django_filters.BooleanFilter()
	userid__abteilung = 		django_filters.CharFilter(lookup_expr='icontains')
	userid__gruppe = 			django_filters.CharFilter(lookup_expr='icontains')
	userid__zi_organisation = 	django_filters.CharFilter(lookup_expr='icontains')


	class Meta:
		model = TblUserhatrolle
		fields = [
			'rollenname', 'userid', 'schwerpunkt_vertretung', 'letzte_aenderung',
			'rollenname__rollenname', 'rollenname__system', 'rollenname__rollenbeschreibung', 'rollenname__datum',
			'userid__geloescht', 'userid__name', 'userid__orga', 'userid__abteilung', 'userid__gruppe',
		]

class UseridFilter(django_filters.FilterSet):
	name = 						django_filters.CharFilter(lookup_expr='istartswith')
	gruppe = 					django_filters.CharFilter(lookup_expr='icontains')

	class Meta:
		model = TblUserIDundName
		fields = [
			'name',
			'userid',
			'zi_organisation',
			'geloescht',
			'abteilung',
			'gruppe',
			'orga',
		]

class RollenFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_expr='istartswith')
	gruppe = django_filters.CharFilter(lookup_expr='icontains')
	rollenname = django_filters.CharFilter(lookup_expr='icontains')
	# afname = django_filters.CharFilter(lookup_expr='icontains')

	class Meta:
		model = TblUserhatrolle
		fields = [
			'userid__name',
			'userid__userid',
			'userid__zi_organisation',
			'userid__gruppe',
			'userid__orga',
			'rollenname',
		]

# Filter für das halbautomatische Selektieren über die Arbeitsplatzfunktion.
# Wird insbesondere in der AF-Factory bei UhR genutzt
class RolleAFFilter(django_filters.FilterSet):
	rollenname = 		django_filters.CharFilter(lookup_expr='istartswith')
	af = 				django_filters.CharFilter(lookup_expr='istartswith')
	af__af_name = 		django_filters.CharFilter(lookup_expr='istartswith')

	class Meta:
		model = TblRollehataf
		fields = [
			'rollenname',
			'rollenname__rollenname',
			'af__af_name',
			'mussfeld',
		]

