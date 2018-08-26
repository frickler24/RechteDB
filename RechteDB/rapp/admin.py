# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from typing import Type, List

from django.contrib import admin

# Register your models here.

# Zum Verändern der Standardeigenschaften eines Textpanes
from django.db import models
from django.forms import Textarea

# Für den Maxwert zum Paginieren
import sys

# Die Datenbanken / Models
from rapp.models import TblUebersichtAfGfs, TblUserIDundName, TblOrga, TblPlattform, \
						TblGesamt, TblGesamtHistorie, Tblrechteneuvonimport, \
						TblRollen, TblAfliste, TblUserhatrolle, TblRollehataf, \
						Tblsubsysteme, Tblsachgebiete, TblDb2, TblRacfGruppen

# Vorwärtsreferenzen gehen nicht in python :-(
# Inline function to show all Instances in other view
class UserhatrolleInline(admin.TabularInline):
	model = TblUserhatrolle
	extra = 0

	fields = ['userundrollenid', 'userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

	formfield_overrides = {
		models.TextField: {
			'widget': Textarea(
				attrs={
					'rows': 1,
					'cols': 40,
					'style': 'height: 1.4em;'
				})},
	}

class GesamtInline(admin.TabularInline):
	model = TblGesamt
	extra = 0

class UserIDundNameInline(admin.TabularInline):
	model = TblUserIDundName
	extra = 0

class RollehatafInline(admin.TabularInline):
	model = TblRollehataf
	extra = 0
	fields = ['af', 'bemerkung', 'mussfeld', 'nurxv', 'xabcv', 'dv', ]

class UebersichtAfGfsInline(admin.TabularInline):
	model = TblUebersichtAfGfs
	extra = 0

class AflisteInline(admin.TabularInline):
	model = TblAfliste
	extra = 0

class RollenInline(admin.TabularInline):
	model = TblRollen
	extra = 0



# ######################################################################################################
# tbl Gesamt
# ######################################################################################################

@admin.register(TblGesamt)
class Gesamt(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	fieldsets = [
		('Standard-Informationen', {'fields': ['userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'modell',
												'plattform', 'gf', 'af_gueltig_bis', 'direct_connect',
												'af_zuweisungsdatum', 'datum', 'geloescht',]}),
		('Detail-Informationen  ', {'fields': ['tf_kritikalitaet', 'tf_eigentuemer_org', 'vip_kennzeichen', 'zufallsgenerator',
												'af_gueltig_ab', 'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung',
												'gefunden', 'wiedergefunden', 'geaendert', 'neueaf', 'nicht_ai',
												'patchdatum', 'wertmodellvorpatch', 'loeschdatum'], 'classes': ['collapse']}),
	]
	list_display = ('id', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'gf',
		'plattform', 'get_direct_connect', 'get_active',
	)
	list_filter = ('geloescht', 'direct_connect', 'userid_name__gruppe', 'plattform', )
	list_display_links = ('id', )
	list_editable = ('tf', 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf', )
	search_fields = ['id', 'userid_name__name', 'tf',
					 # 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf',
	]

	list_per_page = 25

# ######################################################################################################
# tbl UserIDundName
# ######################################################################################################


@admin.register(TblUserIDundName)
class UserIDundNameAdmin(admin.ModelAdmin):

	fieldsets = [
		('User-Informationen', {'fields': ['userid', 'name', 'orga', 'geloescht']}),
		('Orga-Details      ', {'fields': ['zi_organisation', 'abteilung', 'gruppe'], 'classes': ["""'collapse'"""] }),
	]

	list_display = ('id', 'userid', 'colored_name', 'orga', 'zi_organisation', 'get_active', 'abteilung', 'gruppe',)
	list_display_links = ('userid', 'colored_name', 'get_active', )
	list_editable = ('orga', 'zi_organisation', 'abteilung', 'gruppe', )
	search_fields = ['name', 'zi_organisation', 'abteilung', 'gruppe', 'userid']

	list_filter = ('geloescht', 'abteilung', 'gruppe', 'orga', )

	actions_on_top = True
	actions_on_bottom = True

	inlines = [UserhatrolleInline]
	# Nice idea, but VERY slow
	# inlines += [GesamtInline]

	list_per_page = 25
	# inlines = [UserhatrolleInline]


# ######################################################################################################
# tbl Orga
# ######################################################################################################

@admin.register(TblOrga)
class Orga(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True
	list_display = ('team', 'themeneigentuemer', )
	list_filter = ('themeneigentuemer', )
	list_display_links = ('team', )
	list_editable = ('themeneigentuemer', )
	search_fields = ['team',]

	inlines = [UserIDundNameInline]


# ######################################################################################################
# tbl Plattform
# ######################################################################################################

@admin.register(TblPlattform)
class Plattform(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True
	list_display = ('id', 'tf_technische_plattform',)
	# list_filter = ('tf_technische_plattform',)
	# list_display_links = ('tf_technische_plattform')
	list_editable = ('tf_technische_plattform',)
	search_fields = ['tf_technische_plattform', ]

	# Nette Idee, grottig lahm
	# inlines = [GesamtInline]


# ######################################################################################################
# tbl UebersichtAfGfs
# ######################################################################################################

@admin.register(TblUebersichtAfGfs)
class UebersichtAfGfs(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	fieldsets = [
		('Standard       ', {'fields': ['name_af_neu', 'name_gf_neu', 'af_text', 'gf_text',
										'geloescht', 'af_langtext', 'modelliert', ]}),
		('Rechte-Details ', {'fields': ['zielperson', 'kommentar', 'af_ausschlussgruppen', 'af_einschlussgruppen',
										'af_sonstige_vergabehinweise', 'kannweg', ],
							 'classes': ['collapse']}),
	]

	list_display = ('id', 'name_af_neu', 'name_gf_neu', 'af_text', 'gf_text',
					'geloescht', 'af_langtext', 'modelliert', 'zielperson',
					'kommentar', 'af_ausschlussgruppen', 'af_einschlussgruppen',
					'af_sonstige_vergabehinweise', 'kannweg', )

	list_filter = ('geloescht', 'modelliert', 'zielperson', 'kannweg', )

	list_display_links = ()

	list_editable = ('name_af_neu', 'name_gf_neu', 'af_text', 'gf_text', 'af_langtext', 'zielperson', 'kommentar',
					 'af_ausschlussgruppen', 'af_einschlussgruppen', 'af_sonstige_vergabehinweise', )

	search_fields = ['name_af_neu', 'name_gf_neu', 'af_text', 'gf_text', 'af_langtext', ]

	# inlines = [GesamtInline]


# ######################################################################################################
# tbl GesamtHistorie
# ######################################################################################################

@admin.register(TblGesamtHistorie)
class TblGesamtHistorie(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	list_display = ('id', 'id_alt', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'gf',
					'modell', 'tf_kritikalitaet', 'tf_eigentuemer_org', 'plattform',
					'vip_kennzeichen', 'zufallsgenerator', 'datum', 'geloescht', 'gefunden', 'wiedergefunden', 'geaendert', 'neueaf',
					'loeschdatum', )

	search_fields = ['id_alt__id', 'userid_name__name', 'tf', 'tf_beschreibung', 'enthalten_in_af',]


 ######################################################################################################
# tbl Userhatrolle
# ######################################################################################################

@admin.register(TblUserhatrolle)
class Userhatrolle(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True
	actions_selection_counter = True
	list_select_related = True

	formfield_overrides = {
		models.TextField: {
			'widget': Textarea (
				attrs = {
						'rows': 1,
						'cols': 60,
						'style': 'height: 1.4em;'
		})},
	}

	list_display = ('userundrollenid', 'userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', 'letzte_aenderung', )
	list_filter = ('schwerpunkt_vertretung', )
	list_display_links = ('userundrollenid', 'rollenname', )
	list_editable = ('schwerpunkt_vertretung', 'bemerkung', )
	search_fields = [ 'schwerpunkt_vertretung', 'rollenname__rollenname', 'bemerkung', 'userid__name', 'userid__userid', ]

	list_per_page = 25 # sys.maxsize


# ######################################################################################################
# tbl Rollen
# ######################################################################################################

@admin.register(TblRollen)
class Rollen(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	formfield_overrides = {
		models.TextField: {
			'widget': Textarea(
				attrs={
					'rows': 1,
					'cols': 50,
					'style': 'height: 1.4em;'
				})},
	}

	list_display = ('rollenname', 'system', 'rollenbeschreibung', 'datum',)
	list_filter = ('system',)
	list_display_links = ('rollenname',)
	list_editable = ('system', 'rollenbeschreibung', 'rollenbeschreibung',)
	search_fields = ['rollenname', 'system', 'rollenbeschreibung', ]

	inlines = [RollehatafInline, UserhatrolleInline, ]


# ######################################################################################################
# tbl AFListe
# ######################################################################################################

@admin.register(TblAfliste)
class Afliste(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	list_display = ('id', 'af_name', 'neu_ab',)
	# list_display_links = ( 'id', )
	list_editable = ('af_name', )
	search_fields = ['af_name', ]
	# list_filter = ( )

	inlines = [RollehatafInline]


# ######################################################################################################
# tbl RolleHatAF
# ######################################################################################################
# ToDo: Suche AF in Rollen mit Anzeige zugehöriger User
# ToDo: - Suche ist schon erweitert: Anzeige betroffener User integrieren (besser in neuer Abfrage?)

@admin.register(TblRollehataf)
class Rollehataf(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	formfield_overrides = {
		models.TextField: {
			'widget': Textarea (
				attrs = {
						'rows': 1,
						'cols': 40,
						'style': 'height: 1.4em;'
		})},
	}

	list_display = ('rollenmappingid', 'rollenname', 'af', 'get_muss', 'get_nurxv', 'get_xabcv', 'get_dv', 'bemerkung', )
	list_display_links = ('rollenname', )
	list_editable = ('af', 'bemerkung', )		# ToDo die vier Kreuzfelder muss..dv als klickable implementieren
	search_fields = ['rollenname__rollenname', 'af__af_name', 'bemerkung', ]
	list_filter = ('mussfeld', 'nurxv', 'xabcv', 'dv', )

	list_per_page = 20 # sys.maxsize

# ######################################################################################################
# Eine Reihe von Hilfstabellen, alle nach dem selben Schema. Keine Foreign Keys
# ######################################################################################################

@admin.register(Tblsubsysteme)
class Subsysteme(admin.ModelAdmin):
	alle = ['sgss', 'definition', 'verantwortlicher', 'fk',]
	search_fields = alle
	list_display = alle

@admin.register(Tblsachgebiete)		# ToDo Mal eine aktuelle Sachgebiets-/Subsystemtabelle runterladen
class Sachgebiete(admin.ModelAdmin):
	alle = ['sachgebiet', 'definition', 'verantwortlicher', 'fk',]
	search_fields = alle
	list_display = alle

@admin.register(TblDb2)
class Db2(admin.ModelAdmin):
	list_display = ['id', 'get_aktiv', 'source', 'get_grantee', 'creator', 'table',
			'selectauth', 'insertauth', 'updateauth', 'deleteauth',
			'alterauth', 'indexauth', 'grantor', 'grantedts', 'datum']
	search_fields = ['table', 'grantee__group', 'grantor']

@admin.register(TblRacfGruppen)
class RacfGruppen(admin.ModelAdmin):
	alle = ['group', 'test', 'get_produktion', 'get_readonly', 'get_db2_only', 'stempel', ]
	search_fields = alle
	list_display = alle


# Versuch des Im- und Exports via CSV / XLSX / JSON und den Browser
# https://django-import-export.readthedocs.io/en/latest/getting_started.html#admin-integration
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin
class TblrechteneuvonimportResource(resources.ModelResource):
	class Meta:
		model = Tblrechteneuvonimport


from rapp.resources import MyCSVImporterModel
from django.urls import reverse

@admin.register(Tblrechteneuvonimport)
class Tblrechteneuvonimport(ImportExportModelAdmin):
	import_template_name = 'admin/admin_import.html'
	resource_class = MyCSVImporterModel
	alle = ['identitaet', 'nachname', 'vorname', 'tf_name', 'af_anzeigename', 'gf_name', ]
	search_fields = alle
	alle.insert(0, 'id')
	list_display = alle
	list_per_page = 10

