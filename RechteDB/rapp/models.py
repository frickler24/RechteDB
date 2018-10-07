# -*- coding: utf-8 -*-
# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models
from django.utils.html import format_html
from django.urls import reverse		# Used to generate URLs by reversing the URL patterns
from django.utils import timezone
from django.db import connection

# Die drei Rollentabellen sowie die AF-Liste hängen inhaltlich zusammen
# Die Definition der Rollen
class TblRollen(models.Model):
	rollenname = 			models.CharField(db_column='rollenname', primary_key=True, max_length=100, verbose_name='Rollen-Name')
	system = 				models.CharField(db_column='system', max_length=150, verbose_name='System', db_index=True)
	rollenbeschreibung = 	models.TextField(db_column='rollenbeschreibung', blank=True, null=True)
	datum = 				models.DateTimeField(db_column='datum', default=timezone.now, blank=True)

	class Meta:
		managed = True
		db_table = 'tbl_Rollen'
		verbose_name = "Rollenliste"
		verbose_name_plural = "03 Rollen-Übersicht (tbl_Rollen)"
		ordering = [ 'rollenname' ]
		unique_together = (('rollenname', 'system'),)

	def __str__(self) -> str:
		return str(self.rollenname)

# Meta-Tabelle, welche Arbeitsplatzfunktion in welcher Rolle enthalten ist (n:m Beziehung)
#
# Die drei ursprünglichen Einzelfelder nurXV, XABCV und DV wurden zusammengefast zu einer Col: einsatz:
# 	einsatz = 8:	Nur gültig für AV, BV, CV-User (z.B. Zweituser-Recht)
#	einsatz = 4:	Nur gültig für XV-Userid
#	einsatz = 2: 	Gültig für alles außer DV-User
#	einsatz = 1:	Nur gültig für DV-User

class TblRollehataf(models.Model):
	EINSATZ_NONE  = 0
	EINSATZ_NURDV = 1
	EINSATZ_XABCV = 2
	EINSATZ_NURXV = 4
	EINSATZ_ABCV  = 8
	EINSATZ_CHOICES = (
		(EINSATZ_NONE,  'nicht zugewiesen'),
		(EINSATZ_NURDV, 'Nur DV-User'),
		(EINSATZ_XABCV, 'XV, AV, BV, CV'),
		(EINSATZ_NURXV, 'nur XV-User'),
		(EINSATZ_ABCV,  'AV, BV, CV'),
	)

	rollenmappingid = 		models.AutoField(db_column='rollenmappingid', primary_key=True, verbose_name='ID')  # Field name made lowercase.
	rollenname = 			models.ForeignKey('TblRollen', models.PROTECT, to_field='rollenname', db_column='rollenname')  # Field name made lowercase.
	af = 					models.ForeignKey('TblAfliste', models.PROTECT, to_field='id', db_column='af', blank=True, null=True, verbose_name='AF')  # Field name made lowercase.
	mussfeld = 				models.IntegerField(db_column='mussfeld', blank=True, null=True, verbose_name='Muss')  # Field name made lowercase. This field type is a guess.
	bemerkung = 			models.CharField(db_column='bemerkung', max_length=250, blank=True, null=True)  # Field name made lowercase.
	einsatz = 				models.IntegerField(db_column='einsatz', choices=EINSATZ_CHOICES, default=EINSATZ_NONE)

	class Meta:
		managed = True
		db_table = 'tbl_RolleHatAF'
		unique_together = (('rollenname', 'af'),)
		verbose_name = "Rolle und ihre Arbeitsplatzfunktionen"
		verbose_name_plural = "02 Rollen und ihre Arbeitsplatzfunktionen (tbl_RolleHatAF)"
		ordering = [ 'rollenname__rollenname', 'af__af_name', ]

	def __str__(self) -> str:
		return str(self.rollenname)

	def get_muss(self):
		return self.mussfeld
	get_muss.boolean = True
	get_muss.admin_order_field = 'mussfeld'
	get_muss.short_description = 'Muss'
	mussfeld.boolean = True


# Referenz der User auf die ihnen zur Verfügung stehenden Rollen
class TblUserhatrolle(models.Model):
	SCHWERPUNKT_TYPE = (
		('Schwerpunkt', 'Schwerpunktaufgabe'),
		('Vertretung', 'Vertretungstätigkeiten, Zweitsysteme'),
		('Allgemein', 'Rollen, die nicht Systemen zugeordnet sind'),
	)

	userundrollenid = 		models.AutoField(db_column='userundrollenid', primary_key=True, verbose_name='ID')  # Field name made lowercase.
	userid = 				models.ForeignKey('Tbluseridundname', models.PROTECT, to_field='userid', db_column='userid', verbose_name='UserID, Name')  # Field name made lowercase.
	rollenname = 			models.ForeignKey('TblRollen', models.PROTECT, db_column='rollenname')  # Field name made lowercase.

	schwerpunkt_vertretung = \
							models.CharField(db_column='schwerpunkt_vertretung',
											 max_length=100,
											 blank=True, null=True,
											 choices=SCHWERPUNKT_TYPE,
											 db_index=True
							)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	bemerkung = 			models.TextField(db_column='bemerkung', blank=True, null=True)  # Field name made lowercase.
	letzte_aenderung = 		models.DateTimeField(db_column='letzte_aenderung', default=timezone.now, blank=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = True
		db_table = 'tbl_UserHatRolle'
		verbose_name = "User und Ihre Rollen"
		verbose_name_plural = "01 User und Ihre Rollen (tbl_UserHatRolle)"
		ordering = [ 'userid__name', '-userid__userid', 'schwerpunkt_vertretung', 'rollenname', ]
		unique_together = (('userid', 'rollenname'),)

	def __str__(self) -> str:
		return str(self.userundrollenid)		# ToDo: Stimmt das?

	def get_rollenbeschreibung (self):
		return str(self.rollenname.rollenbeschreibung)
	get_rollenbeschreibung.short_description = 'Rollenbeschreibung'

	def get_absolute_url(self):
		# Returns the url for the whole list.
		return reverse('user_rolle_af', args=[])

	def get_absolute_update_url(self):
		# Returns the url to access a particular instance of the model.
		return reverse('user_rolle_af-update', args=[str(self.id)])

	def get_absolute_create_url(self):
		# Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
		return reverse('user_rolle_af-create', args=[])

	def get_absolute_delete_url(self):
		# Returns the url to access a particular instance of the model.
		return reverse('user_rolle_af-delete', args=[str(self.userundrollenid)])



# Tabelle enthält die aktuell genehmigten (modellierten und in Modellierung befindlichen) AF + GF-Kombinationen
class TblUebersichtAfGfs(models.Model):
	id = 					models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	name_gf_neu = 			models.CharField(db_column='name_gf_neu', max_length=50, verbose_name='GF Neu', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	name_af_neu = 			models.CharField(db_column='name_af_neu', max_length=50, verbose_name='AF Neu', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	kommentar = 			models.CharField(db_column='kommentar', max_length=150, blank=True, null=True)  # Field name made lowercase.
	zielperson = 			models.CharField(db_column='zielperson', max_length=50, )  # Field name made lowercase.
	af_text = 				models.CharField(db_column='af_text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_text = 				models.CharField(db_column='gf_text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_langtext = 			models.CharField(db_column='af_langtext', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_ausschlussgruppen = 	models.CharField(db_column='af_ausschlussgruppen', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_einschlussgruppen = 	models.CharField(db_column='af_einschlussgruppen', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_sonstige_vergabehinweise = models.CharField(db_column='af_sonstige_vergabehinweise', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht =				models.IntegerField(db_column='geloescht', blank=True, null=True, db_index=True)
	kannweg = 				models.IntegerField(blank=True, null=True)
	modelliert = 			models.DateTimeField(blank=True, null=True)

	class Meta:
		managed = True
		db_table = 'tblUEbersichtAF_GFs'
		unique_together = (('name_af_neu', 'name_gf_neu'), ('name_gf_neu', 'name_af_neu'), )
		verbose_name = "Erlaubte AF/GF-Kombination"
		verbose_name_plural = "04 Erlaubte AF/GF-Kombinationen-Übersicht (tblUebersichtAF_GFs)"
		ordering = ['-id']

	def __str__(self) -> str:
		return self.name_gf_neu + ' | ' + self.name_af_neu

	geloescht.boolean = True
	kannweg.boolean = True

# Die Tabelle enthält die Teambeschreibungen. Das eigentliche Team ist das Feld intern_extern
class TblOrga(models.Model):
	id = 				models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	team = 				models.CharField(db_column='team', unique=True, max_length=64, blank=False, null=False, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	themeneigentuemer =	models.CharField(db_column='themeneigentuemer', max_length=64, blank=False, null=False, db_index=True)  # Field name made lowercase.

	class Meta:
		managed = True
		db_table = 'tblOrga'
		verbose_name = "Orga-Information"
		verbose_name_plural = "06 Organisations-Übersicht (tblOrga)"
		ordering = ['team']

	def __str__(self) -> str:
		return self.team

	def get_absolute_url(self):
		# Returns the url for the item.
		return reverse('teamliste', args=[])

	def get_absolute_update_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('team-update', args=[str(self.id)])

	def get_absolute_delete_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('team-delete', args=[str(self.id)])

	def get_absolute_create_url(self):
		# Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
		return reverse('team-create', args=[])

# Die Namen aller aktiven und gelöschten UserIDen und der dazugehörenden Namen (Realnamen und Technische User)
class TblUserIDundName(models.Model):
	id = 				models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	userid = 			models.CharField(db_column='userid', max_length=32, unique=True)  # Field name made lowercase.
	name = 				models.CharField(db_column='name', max_length=75, )  # Field name made lowercase.
	orga = 				models.ForeignKey('TblOrga', db_column='orga_id', on_delete=models.CASCADE, verbose_name='Team', db_index=True)  # Field name made lowercase.
	zi_organisation =	models.CharField(db_column='zi_organisation', max_length=64, verbose_name='ZI-Organisation', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht = 		models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht', db_index=True)
	abteilung = 		models.CharField(db_column='abteilung', max_length=64, )  # Field name made lowercase.
	gruppe = 			models.CharField(db_column='gruppe', max_length=32, db_index=True)  # Field name made lowercase.

	class Meta:
		managed = True
		db_table = 'tblUserIDundName'
		index_together = (('gruppe', 'geloescht'),)
		verbose_name = "UserID-Name-Kombination"
		verbose_name_plural = "05 UserID-Name-Übersicht (tblUserIDundName)"
		ordering = ['geloescht', 'name', '-userid']
		unique_together = (('userid', 'name'),)
		index_together = (('geloescht', 'name', 'userid'),)

	def __str__(self) -> str:
		return str(self.userid + ' | ' + self.name)

	def get_active(self):
		return not self.geloescht
	get_active.boolean = True
	get_active.admin_order_field = 'geloescht'
	get_active.short_description = 'aktiv'

	geloescht.boolean = True

	def colored_name(self):
		return format_html(
			'<span style="color: #{};">{}</span>',
			'21610B' if (self.get_active()) else "B40404",
			self.name,
		)
	colored_name.admin_order_field= 'name'
	colored_name.short_description = 'Name, Vorname'

	def get_absolute_url(self):
		# Returns the url for the whole list.
		return reverse('userliste', args=[])

	def get_absolute_update_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-update', args=[str(self.id)])

	def get_absolute_toggle_geloescht_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-toggle-geloescht', args=[str(self.id)])

	def get_absolute_delete_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-delete', args=[str(self.id)])

	def get_absolute_create_url(self):
		# Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
		return reverse('user-create', args=[])

# Diese Funktion gehört inhaltlich zu tblUserIDundName, aber nicht in die Klasse (wird in form.py genutzt)
def hole_organisationen():
	# Liefert eine Liste an Tupeln mit Choices für die Orga-Auswahl zurück. Die Liste stammt aus tblUserIDundName.
	with connection.cursor() as cursor:
		cursor.execute("SELECT DISTINCT zi_organisation FROM tblUserIDundName")
		rows = cursor.fetchall()
		return [('Bitte Organisation wählen', 'Bitte Organisation wählen')] + [(r[0], r[0]) for r in rows]

# Die verschiedenen technischne Plattformen (RACF, CICS, Unix, Win, AD, LDAP, test/Prod usw.)
class TblPlattform(models.Model):
	id = 						models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	tf_technische_plattform = 	models.CharField(db_column='tf_technische_plattform', unique=True, max_length=32, verbose_name='Plattform', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = True
		db_table = 'tblPlattform'
		verbose_name = "Plattform"
		verbose_name_plural = "07 Plattform-Übersicht (tblPlattform)"
		ordering = ['tf_technische_plattform']

	def __str__(self) -> str:
		return self.tf_technische_plattform

# tblGesamt enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen
class TblGesamt(models.Model):
	id = 					models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	userid_name = 			models.ForeignKey('TblUserIDundName', db_column='userid_und_name_id', on_delete=models.CASCADE, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf = 					models.CharField(db_column='tf', max_length=100, verbose_name='TF', db_index=True)  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='tf_beschreibung', max_length=250, blank=True, null=True, verbose_name='TF-Beschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True, verbose_name='AF', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	modell = 				models.ForeignKey('TblUebersichtafGfs', db_column='modell', on_delete=models.CASCADE, db_index=True)  # Field name made lowercase.
	tf_kritikalitaet = 		models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True, verbose_name='TF-Kritikalität', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = 	models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True, verbose_name='TF-Eigentümer-orga', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	plattform = 			models.ForeignKey('TblPlattform', db_column='plattform_id', on_delete=models.CASCADE, verbose_name='Plattform', db_index=True)  # Field name made lowercase.
	gf = 					models.CharField(db_column='gf', max_length=100, blank=True, null=True, verbose_name='GF', db_index=True)  # Field name made lowercase.
	vip_kennzeichen = 		models.CharField(db_column='vip', max_length=32, blank=True, null=True, verbose_name='VIP')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = 		models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True, verbose_name='Zufallsgenerator')  # Field name made lowercase.
	af_gueltig_ab = 		models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True, verbose_name='AF gültig ab')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True, verbose_name='AF gültig bis')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='direct_connect', max_length=100, blank=True, null=True, verbose_name='Direktverbindung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = \
							models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True, verbose_name='max. Krit. TF in AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = 		models.CharField(db_column='gf_beschreibung', max_length=250, blank=True, null=True, verbose_name='GF Kurzbeschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = 	models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True, verbose_name='AF Zuweisung', db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	datum = 				models.DateTimeField(db_column='datum', verbose_name='Recht gefunden am', db_index=True)  # Field name made lowercase.
	geloescht = 			models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht', db_index=True)
	gefunden = 				models.IntegerField(blank=True, null=True, db_index=True)
	wiedergefunden = 		models.DateTimeField(blank=True, null=True, db_index=True)
	geaendert = 			models.IntegerField(db_column='geaendert', blank=True, null=True, verbose_name='AF geändert', db_index=True)  # This field type is a guess.
	neueaf = 				models.CharField(db_column='neueaf', max_length=50, blank=True, null=True, db_index=True)  # Field name made lowercase.
	nicht_ai = 				models.IntegerField(db_column='nicht_ai', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	patchdatum = 			models.DateTimeField(db_column='patchdatum', blank=True, null=True, db_index=True)  # Field name made lowercase.
	wertmodellvorpatch =	models.TextField(db_column='wert_modell_vor_patch', blank=True, null=True)  # Field name made lowercase.
	loeschdatum = 			models.DateTimeField(db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum', db_index=True)
	letzte_aenderung = 		models.DateTimeField(auto_now=True, db_index=True)

	class Meta:
		managed = True
		db_table = 'tblGesamt'
		verbose_name = "Eintrag der Gesamttabelle (tblGesamt)"
		verbose_name_plural = "08 Gesamttabelle Übersicht (tblGesamt)"
		index_together = (('userid_name', 'tf', 'enthalten_in_af', 'plattform', 'gf', 'vip_kennzeichen', 'zufallsgenerator'),)
		ordering = ['id']

	def __str__(self) -> str:
		return str(self.id)

	def get_active(self):
		return not self.geloescht
	get_active.boolean = True
	get_active.admin_order_field = 'geloescht'
	get_active.short_description = 'aktiv'

	def get_gefunden(self):
		return self.gefunden
	get_gefunden.boolean = True

	def get_geaendert(self):
		return self.geaendert
	geaendert.boolean = True

	def get_direct_connect(self):
		return self.direct_connect == 'Ja'
	get_direct_connect.boolean = True
	get_direct_connect.admin_order_field = 'direct_connect'
	get_direct_connect.short_description = 'direkt'

	def get_ai(self):
		return not self.nicht_ai
	get_ai.boolean = True

	def get_absolute_url(self):
		# Returns the url to access a particular instance of the model.
		return reverse('gesamt-detail', args=[str(self.id)])

# tblGesamtHistorie enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen, wenn der User (mal) gelöscht wurde
class TblGesamtHistorie(models.Model):
	id = 				models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	id_alt = 			models.IntegerField(db_column='id_alt', blank=False, null=False, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	userid_name = 		models.ForeignKey('TblUserIDundName', models.PROTECT, db_column='userid_und_name_id', to_field='id', )  # Field name made lowercase. Field renamed to remove unsuitable characters.

	tf = 					models.CharField(db_column='tf', max_length=100, verbose_name='TF')  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='tf_beschreibung', max_length=300, blank=True, null=True, verbose_name='TF-Beschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True, verbose_name='AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	modell = 				models.ForeignKey('TblUebersichtafGfs', db_column='modell', on_delete=models.CASCADE)  # Field name made lowercase.
	tf_kritikalitaet = 		models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True, verbose_name='TF-Kritikalität')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = 	models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True, verbose_name='TF-Eigentümer-orga')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	plattform = 			models.ForeignKey('TblPlattform', db_column='plattform_id', on_delete=models.CASCADE, verbose_name='Plattform')  # Field name made lowercase.
	gf = 					models.CharField(db_column='gf', max_length=100, blank=True, null=True, verbose_name='GF')  # Field name made lowercase.
	vip_kennzeichen = 		models.CharField(db_column='vip', max_length=32, blank=True, null=True, verbose_name='VIP')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = 		models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True, verbose_name='Zufallsgenerator')  # Field name made lowercase.

	datum = 				models.DateTimeField(db_column='datum', verbose_name='Recht gefunden am')  # Field name made lowercase.
	geloescht = 			models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht')
	gefunden = 				models.IntegerField(blank=True, null=True)
	wiedergefunden = 		models.DateTimeField(blank=True, null=True)
	geaendert = 			models.IntegerField(db_column='geaendert', blank=True, null=True, verbose_name='AF geändert')  # This field type is a guess.
	neueaf = 				models.CharField(db_column='neueaf', max_length=50, blank=True, null=True, db_index=True)  # Field name made lowercase.
	loeschdatum = 			models.DateTimeField(db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum')
	af_zuweisungsdatum = 	models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True, verbose_name='AF Zuweisung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	# ToDo: überlegen, ob af_zuweisungsdatum_alt weg kann oder wozu es genutzt werden soll
	af_zuweisungsdatum_alt =\
							models.DateTimeField(db_column='af_zuweisungsdatum_alt', blank=True, null=True, verbose_name='AF Zuweisung alt')  # Field name made lowercase. Field renamed to remove unsuitable characters.

	af_gueltig_ab = 		models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True, verbose_name='AF gültig ab')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True, verbose_name='AF gültig bis')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='direct_connect', max_length=100, blank=True, null=True, verbose_name='Direktverbindung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = \
							models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True, verbose_name='max. Krit. TF in AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = 		models.CharField(db_column='gf_beschreibung', max_length=300, blank=True, null=True, verbose_name='GF Kurzbeschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	nicht_ai = 				models.IntegerField(db_column='nicht_ai', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	patchdatum = 			models.DateTimeField(db_column='patchdatum', blank=True, null=True, )  # Field name made lowercase.
	wertmodellvorpatch =	models.TextField(db_column='wert_modell_vor_patch', blank=True, null=True)  # Field name made lowercase.
	letzte_aenderung = 		models.DateTimeField(blank=True, null=True)


	class Meta:
		managed = True
		db_table = 'tblGesamtHistorie'
		verbose_name = "Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)"
		verbose_name_plural = "99 Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)"

	def __str__(self) -> str:
		return str(self.id)

# Dies ist nur eine Hilfstabelle.
# Sie besteht aus dem `tblÜbersichtAF_GFs`.`Name AF Neu` für alle Felder, bei denen `modelliert` nicht null ist.
# (das automatisch ergänzte Datum wird nicht benötigt, hier könnte auch das `modelliert`genommen werden)
# Original Query im Access:_
#
# INSERT INTO tbl_AFListe ( [AF-Name] )
#  SELECT tblÜbersichtAF_GFs.[Name AF Neu]
#  FROM tblÜbersichtAF_GFs LEFT JOIN tbl_AFListe ON tblÜbersichtAF_GFs.[Name AF Neu] = tbl_AFListe.[AF-Name]
#  WHERE (((tblÜbersichtAF_GFs.modelliert) Is Not Null) AND ((tbl_AFListe.[AF-Name]) Is Null))
#  GROUP BY tblÜbersichtAF_GFs.[Name AF Neu];
#
# Sinn der Tabelle ist, eine eindeutige Liste an AFs vorliegen zu haben. Das GROUP- BY kann evtl teuer werden.
# Aber das probieren wir jetzt mal aus.
class TblAfliste(models.Model):		# ToDo: Wegwerfen, Tabelle könnte eventuell ersetzt werden durch eine geeignete View (order by auf AF_Name)
	id = 					models.AutoField(db_column='id', primary_key=True, verbose_name='ID')  # Field name made lowercase.
	af_name = 				models.CharField(db_column='af_name', unique=True, max_length=150, verbose_name='AF-Name')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	neu_ab = 				models.DateTimeField(db_column='neu_ab')  # Field renamed to remove unsuitable characters.

	class Meta:
		managed = True
		db_table = 'tbl_AFListe'
		verbose_name = "Gültige AF"
		verbose_name_plural = "98 Übersicht gültiger AFen (tbl_AFListe)"
		ordering = [ 'af_name' ]

	def __str__(self) -> str:
		return str(self.af_name)

###################################### Tblsubsysteme, Tblsachgebiete, TblDb2
# Ein paar Hilfstabellen.
# Die sind inhaltlich wahrscheinlich nicht super aktuell, helfen aber bei verschiedenen Fragen.
# Leider müssen die Modelle und ihre Columns so heißen, wie ihre Übreschriften es vorgeben (kein SQL-Standard)

class Tblsachgebiete(models.Model):
	sachgebiet = models.CharField(db_column='Sachgebiet', primary_key=True, max_length=32)  # Field name made lowercase.
	definition = models.CharField(db_column='Definition', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	verantwortlicher = models.CharField(db_column='Verantwortlicher', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	telefon_verantwortlicher = models.CharField(db_column='Telefon', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	user_id_verantwortlicher = models.CharField(db_column='user_id', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	fk = models.CharField(db_column='Führungskraft', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

	class Meta:
		managed = True
		db_table = 'tblSachgebiete'
		verbose_name = "Sachgebiet"
		verbose_name_plural = "51 Übersicht Sachgebiete (tbl_Sachgebiete)"
		ordering = ['sachgebiet']

class Tblsubsysteme(models.Model):
	sgss = models.CharField(db_column='sgss', primary_key=True, max_length=32)  # Field name made lowercase.
	definition = models.CharField(db_column='Definition', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	verantwortlicher = models.CharField(db_column='Verantwortlicher', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	telefon_verantwortlicher = models.CharField(db_column='Telefon', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	user_id_verantwortlicher = models.CharField(db_column='user_id', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
	fk = models.CharField(db_column='Führungskraft', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

	class Meta:
		managed = True
		db_table = 'tblSubsysteme'
		verbose_name = "Subsystem"
		verbose_name_plural = "50 Übersicht Subsysteme (tbl_Subsysteme)"
		ordering = [ 'sgss' ]

class TblDb2(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	geloescht = models.TextField(db_column='geloescht', blank=True, null=True, )  # This field type is a guess.
	source = models.CharField(db_column='source', max_length=15, blank=True, null=True)  # Field name made lowercase.
	grantee = models.ForeignKey('TblRacfGruppen', models.PROTECT, to_field='group', db_column='grantee')  # Field name made lowercase.
	creator = models.CharField(db_column='CREATOR', max_length=15, blank=True, null=True)  # Field name made lowercase.
	table = models.CharField(db_column='TABLE', max_length=31, db_index=True)  # Field name made lowercase.
	selectauth = models.CharField(db_column='SELECTAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	insertauth = models.CharField(db_column='INSERTAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	updateauth = models.CharField(db_column='UPDATEAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	deleteauth = models.CharField(db_column='DELETEAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	alterauth = models.CharField(db_column='ALTERAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	indexauth = models.CharField(db_column='INDEXAUTH', max_length=3, blank=True, null=True)  # Field name made lowercase.
	grantor = models.CharField(db_column='GRANTOR', max_length=15, db_index=True)  # Field name made lowercase.
	grantedts = models.CharField(db_column='GRANTEDTS', max_length=63)  # Field name made lowercase.
	datum = models.DateTimeField()

	class Meta:
		managed = True
		db_table = 'tbl_DB2'
		verbose_name = 'DB2-Berechtigung'
		verbose_name_plural = '52 DB2 - Berechtigungen (Tbl_DB2)'
		ordering = [ 'id', ]

	def __str__(self) -> str:
		return self.id

	def get_grantee(self):
		return str(self.grantee.group)
	get_grantee.admin_order_field = 'grantee'
	get_grantee.short_description = 'Grantee'

	def get_aktiv(self):
		return not self.geloescht
	get_aktiv.admin_order_field = 'geloescht'
	get_aktiv.short_description = 'Aktiv'

class TblRacfGruppen(models.Model):
	group = models.CharField(db_column='Group', primary_key=True, max_length=150)  # Field name made lowercase.
	test = models.IntegerField(db_column='Test', blank=True, null=True, db_index=True)  # Field name made lowercase. This field type is a guess.
	produktion = models.IntegerField(db_column='Produktion', blank=True, null=True, db_index=True)  # Field name made lowercase. This field type is a guess.
	readonly = models.IntegerField(db_column='Readonly', blank=True, null=True, db_index=True)  # Field name made lowercase. This field type is a guess.
	db2_only = models.IntegerField(db_column='DB2-only', blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. This field type is a guess.
	stempel = models.DateTimeField(db_column='Stempel', db_index=True)  # Field name made lowercase.

	def __str__(self) -> str:
		return str(self.group)

	class Meta:
		managed = True
		db_table = 'tbl_RACF_Gruppen'
		verbose_name = 'RACF-Berechtigung'
		verbose_name_plural = '53 RACF - Berechtigungen (tbl_DB2)'
		ordering = [ 'group', ]

	def get_test(self):
		return int(self.test)
	get_test.boolean = True
	get_test.admin_order_field = 'test'
	get_test.short_description = 'Test'

	def get_produktion(self):
		return int(self.produktion)
	get_produktion.boolean = True
	get_produktion.admin_order_field = 'produktion'
	get_produktion.short_description = 'Produktion'

	def get_readonly(self):
		return int(self.readonly)
	get_readonly.boolean = True
	get_readonly.admin_order_field = 'readonly'
	get_readonly.short_description = 'Read only'

	def get_db2_only(self):
		return int(self.db2_only)
	get_db2_only.boolean = True
	get_db2_only.admin_order_field = 'db2_only'
	get_db2_only.short_description = 'DB2 only'

###################################### Tblsubsysteme, Tblsachgebiete, TblDb2
# Tabellen für den Import neuer Listen
# Diese Tabellenspalten bleiben auf ihrem teilweise nicht SQL-konformem Namen,
# weil sie als Importspalten für die csv / xls-Datein benötigt werden.
# Gegebenenfalls kann das später noch angepasst werden.

class Tblrechteneuvonimport(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	identitaet = models.CharField(db_column='Identität', max_length=150, blank=False, null=False, db_index=True)  # Field name made lowercase.
	nachname = models.CharField(db_column='Nachname', max_length=150, blank=True, null=True)  # Field name made lowercase.
	vorname = models.CharField(db_column='Vorname', max_length=150, blank=True, null=True)  # Field name made lowercase.
	tf_name = models.CharField(db_column='TF Name', max_length=100, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_beschreibung = models.CharField(db_column='TF Beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_anzeigename = models.CharField(db_column='AF Anzeigename', max_length=100, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_beschreibung = models.CharField(db_column='AF Beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='Höchste Kritikalität TF in AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = models.CharField(db_column='TF Eigentümer Org', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_applikation = models.CharField(db_column='TF Applikation', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_kritikalitaet = models.CharField(db_column='TF Kritikalität', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_name = models.CharField(db_column='GF Name', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = models.CharField(db_column='GF Beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = models.CharField(db_column='Direct Connect', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zugewiesen_an_account_name = models.CharField(db_column='AF zugewiesen an Account-Name', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_ab = models.DateTimeField(db_column='AF Gültig ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = models.DateTimeField(db_column='AF Gültig bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = models.DateTimeField(db_column='AF Zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = True
		db_table = 'tblRechteNeuVonImport'
		verbose_name = 'Importiere neue Daten (tblRechteNeuVonImport)'
		verbose_name_plural = 'Importiere neue Daten (tblRechteNeuVonImport)'
		ordering = [ 'id', ]

class Tblrechteamneu(models.Model):
	id = 					models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
	userid = 				models.CharField(db_column='userid', max_length=50, blank=True, null=True, db_index=True)  # Field name made lowercase.
	name = 					models.CharField(db_column='name', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	tf = 					models.CharField(db_column='tf', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='tf_beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_kritikalitaet = 		models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = 	models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_technische_plattform =\
							models.CharField(db_column='tf_technische_plattform', max_length=64, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf = 					models.CharField(db_column='gf', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	vip_kennzeichen = 		models.CharField(db_column='vip', max_length=32, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = 		models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True, db_index=True)  # Field name made lowercase.
	af_gueltig_ab = 		models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='direct_connect', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af =\
							models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = 		models.CharField(db_column='gf_beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = 	models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gefunden = 				models.IntegerField(db_column='gefunden', blank=True, null=True, db_index=True)  # Field name made lowercase.
	geaendert = 			models.IntegerField(db_column='geaendert', blank=True, null=True, db_index=True)  # Field name made lowercase.
	angehaengt_bekannt = 	models.IntegerField(db_column='angehaengt_bekannt', blank=True, null=True, db_index=True)  # Field name made lowercase.
	angehaengt_sonst = 		models.IntegerField(db_column='angehaengt_sonst', blank=True, null=True, db_index=True)  # Field name made lowercase.
	doppelerkennung = 		models.IntegerField(blank=True, null=True)

	class Meta:
		managed = True
		db_table = 'tblRechteAMNeu'
		unique_together = (('userid', 'tf', 'enthalten_in_af', 'tf_technische_plattform', 'gf'),)

class Qryf3Rechteneuvonimportduplikatfrei(models.Model):
	userid = 				models.CharField(db_column='userid', max_length=32, blank=True, null=True, db_index=True)  # Field name made lowercase.
	name = 					models.CharField(db_column='name', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	tf = 					models.CharField(db_column='tf', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='tf_beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_kritikalitaet = 		models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = 	models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_technische_plattform =\
							models.CharField(db_column='tf_technische_plattform', max_length=32, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf = 					models.CharField(db_column='gf', max_length=100, blank=True, null=True, db_index=True)  # Field name made lowercase.
	vip_kennzeichen = 		models.CharField(db_column='vip', max_length=8, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = 		models.CharField(db_column='zufallsgenerator', max_length=8, blank=True, null=True, db_index=True)  # Field name made lowercase.
	af_gueltig_ab = 		models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='direct_connect', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af =\
							models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True, db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = 		models.CharField(db_column='gf_beschreibung', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = 	models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = True
		db_table = 'qryF3_RechteNeuVonImportDuplikatfrei'
		unique_together = (('userid', 'tf', 'enthalten_in_af', 'tf_technische_plattform', 'gf'),)
