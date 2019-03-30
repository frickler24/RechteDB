# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from typing import Type, List

from django.contrib import admin

# Register your models here.

# Zum Verändern der Standardeigenschaften eines Textpanes
from django.db import models
from django.forms import Textarea

# Die Datenbanken / Models
from rapp.models import TblUebersichtAfGfs, TblUserIDundName, TblOrga, TblPlattform, \
						TblGesamt, TblGesamtHistorie, Tblrechteneuvonimport, \
						TblRollen, TblAfliste, TblUserhatrolle, TblRollehataf, \
						Tblsubsysteme, Tblsachgebiete, TblDb2, TblRacfGruppen, \
						RACF_Rechte, Orga_details, \
						Modellierung

# Für den Im- und Export
from import_export.admin import ImportExportModelAdmin
from rapp.resources import MeinCSVImporterModel, GesamtExporterModel, ModellierungExporterModel

# Vorwärtsreferenzen gehen nicht in python :-(
# Inline function to show all Instances in other view
class UserhatrolleInline(admin.TabularInline):
	model = TblUserhatrolle
	extra = 1

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
	extra = 1

class RollehatafInline(admin.TabularInline):
	model = TblRollehataf
	extra = 1
	fields = ['af', 'bemerkung', 'mussfeld', 'einsatz', ]

class UebersichtAfGfsInline(admin.TabularInline):
	model = TblUebersichtAfGfs
	extra = 1

class AflisteInline(admin.TabularInline):
	model = TblAfliste
	extra = 1

class RollenInline(admin.TabularInline):
	model = TblRollen
	extra = 1

# ######################################################################################################
# tbl Gesamt
# ######################################################################################################
@admin.register(TblGesamt)
class GesamtAdmin(ImportExportModelAdmin):
	actions_on_top = False		# Keine Actions, weil diese Tabelle nie manuell geändert wird
	actions_on_bottom = False

	list_select_related = ('modell', 'userid_name', 'plattform', )

	# Diese Fieldsets greifen bei Detailsichten zu Änderungen und Neuanlagen von Einträgen.
	# Braucht so eigentlich niemand...
	fieldsets = [
		('Standard-Informationen', {'fields': ['userid_name', 'tf', 'tf_beschreibung',
											   	'enthalten_in_af', 'modell',
												'plattform', 'gf', 'af_gueltig_bis', 'direct_connect',
												'af_zuweisungsdatum', 'datum', 'geloescht', ]}),
		('Detail-Informationen  ', {'fields': ['tf_kritikalitaet', 'tf_eigentuemer_org',
											   	'vip_kennzeichen', 'zufallsgenerator',
												'af_gueltig_ab', 'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung',
												'gefunden', 'wiedergefunden', 'geaendert', 'neueaf', 'nicht_ai',
												'patchdatum', 'wertmodellvorpatch', 'loeschdatum', ],
												'classes': ['collapse']}),
	]
	list_display = ('id', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'gf',
		'plattform', 'get_direct_connect', 'get_active',
	)
	list_filter = ('geloescht', 'direct_connect', 'userid_name__gruppe', 'plattform', )
	list_display_links = ('id', )
	list_editable = ('tf', 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf', )
	search_fields = ['id', 'userid_name__name', 'tf',
					'tf_beschreibung', #'enthalten_in_af', 'plattform', 'gf',
	]

	list_per_page = 50

	# Parameter für import/export
	resource_class = GesamtExporterModel
	sortable_by = ['userid_name']

# ######################################################################################################
# tbl UserIDundName
# ######################################################################################################
@admin.register(TblUserIDundName)
class UserIDundNameAdmin(admin.ModelAdmin):

	list_select_related = ('orga', )

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
	# Nette Idee, grottig lahm
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
	actions_on_top = False
	actions_on_bottom = False

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
						'cols': 40,
						'style': 'height: 1.4em;'
		})},
	}

	list_display = ('userundrollenid', 'userid', 'rollenname', 'schwerpunkt_vertretung',
					'get_rollenbeschreibung', 'bemerkung', 'letzte_aenderung', )
	list_filter = ('schwerpunkt_vertretung', )
	list_display_links = ('userundrollenid', 'rollenname', )
	list_editable = ('schwerpunkt_vertretung', 'bemerkung', )
	search_fields = [ 'schwerpunkt_vertretung', 'rollenname__rollenname', 'bemerkung', 'userid__name', 'userid__userid', ]

	list_per_page = 25 # sys.maxsize
	extra = 1

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
	extra = 1

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

	list_display = ('rollenmappingid', 'rollenname', 'af', 'get_muss', 'einsatz', 'bemerkung', )
	list_display_links = ('rollenname', )
	list_editable = ('af', 'bemerkung', )
	search_fields = ['rollenname__rollenname', 'af__af_name', 'bemerkung', ]
	list_filter = ('mussfeld', 'einsatz', )

	list_per_page = 25 # sys.maxsize

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
	list_display = ['id', 'source', 'grantee', 'creator', 'table',
			'selectauth', 'insertauth', 'updateauth', 'deleteauth', 'alterauth', 'indexauth',
			'grantor', 'grantedts', 'datum']
	search_fields = ['table', 'grantee', 'grantor']
	list_filter = ('source', 'datum')

# Wahrscheinlich kann die DB mal entsorgt werden.
# Sie war ursprünglich entwickelt worden, um die Frage der SE zu beantworten,
# welche Rechte in Produktion Schreibrechte sind.
# ToDo Tabelle RacfGruppen entsorgen, wenn sie bis Jahresmitte 2019 nicht mehr benötigt wurde
#@admin.register(TblRacfGruppen)
class RacfGruppen(admin.ModelAdmin):
	alle = ['group', 'test', 'get_produktion', 'get_readonly', 'get_db2_only', 'stempel', ]
	search_fields = alle
	list_display = alle

@admin.register(RACF_Rechte)
class RACF_Rechte(admin.ModelAdmin):
	alle = ['id', 'type', 'group', 'ressource_class', 'profil', 'access',
			'test', 'produktion', 'alter_control_update', 'datum', ]
	search_fields = alle
	list_display = alle

@admin.register(Orga_details)
class Orga_details(admin.ModelAdmin):
	alle = ['id', 'abteilungsnummer', 'organisation', 'orgaBezeichnung',
			'fk', 'kostenstelle', 'orgID', 'parentOrga', 'parentOrgID',
			'orgaTyp', 'fkName', 'delegationEigentuemer', 'delegationFK',
			'datum', ]
	search_fields = alle
	list_display = alle

@admin.register(Modellierung)
class Modellierung(ImportExportModelAdmin):
	alle = [
		'entitlement', 'neue_beschreibung', 'plattform', 'gf',
		'beschreibung_der_gf', 'af', 'beschreibung_der_af',
		'organisation_der_af', 'eigentuemer_der_af',
		'aus_modellierung_entfernen', 'datei', 'letzte_aenderung'
	]
	search_fields = alle
	list_display = alle
	list_editable = () # Read Only Tabelle

	# Parameter für import/export
	resource_class = ModellierungExporterModel
	sortable_by = ['entitlement', 'plattform', 'gf', 'af']
