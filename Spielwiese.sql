SELECT
    `tblGesamt`.`ID` AS `ID`,
    `tblUserIDundName`.`Gruppe` AS `Gruppe`,
    `tblUserIDundName`.`Orga_ID` AS `Orga_ID`,
    `tblGesamt`.`UserID + Name_ID` AS `UserID + Name_ID`,
    `tblGesamt`.`TF` AS `TF`,
    `tblGesamt`.`TF Beschreibung` AS `TF Beschreibung`,
    `tblGesamt`.`Enthalten in AF` AS `Enthalten IN AF`,
    `tblGesamt`.`Modell` AS `Modell`,
    `tblGesamt`.`Plattform_ID` AS `Plattform_ID`,
    `tblGesamt`.`GF` AS `GF`,
    `tblGesamt`.`GF Beschreibung` AS `GF Beschreibung`,
    `tblGesamt`.`gelöscht` AS `gelöscht`,
    `tblGesamt`.`löschdatum` AS `löschdatum`,
    `tblGesamt`.`AF Gültig ab` AS `AF Gültig ab`,
    `tblGesamt`.`AF Gültig bis` AS `AF Gültig bis`,
    `tblGesamt`.`Direct Connect` AS `Direct Connect`,
    `tblGesamt`.`Höchste Kritikalität TF in AF` AS `Höchste Kritikalität TF IN AF`,
    `tblGesamt`.`AF Zuweisungsdatum` AS `AF Zuweisungsdatum`,
    `tbl_RACF_Gruppen`.`Test` AS `Test`,
    `tbl_RACF_Gruppen`.`Produktion` AS `Produktion`,
    `tbl_RACF_Gruppen`.`Readonly` AS `Readonly`,
    `tblGesamt`.`TF Kritikalität` AS `TF Kritikalität`,
    `tblGesamt`.`TF Eigentümer Org` AS `TF Eigentümer Org`,
    `tblUserIDundName`.`ZI-Organisation` AS `ZI-Organisation`,
    `tblGesamt`.`Datum` AS `Datum`,
    `tblGesamt`.`gefunden` AS `gefunden`,
    `tblGesamt`.`wiedergefunden` AS `wiedergefunden`,
    `tblGesamt`.`geändert` AS `geändert`,
    `tblGesamt`.`NeueAF` AS `NeueAF`,
    `tblUserIDundName`.`UserID` AS `UserID`,
    `tblUserIDundName`.`Name` AS `Name`,
    `tblGesamt`.`VIP Kennzeichen` AS `VIP Kennzeichen`,
    `tblGesamt`.`Zufallsgenerator` AS `Zufallsgenerator`
FROM
    (
    `tblÜbersichtAF_GFs`
    JOIN(
            `tblPlattform`
        JOIN(
                (
                    (
                    `tblUserIDundName`
                    JOIN `tblGesamt` ON
                        (
                            (
                                (`tblUserIDundName`.`gelöscht` <> 1) AND(
                                    `tblUserIDundName`.`ID` = `tblGesamt`.`UserID + Name_ID`
                                )
                            )
                        )
                    )
                LEFT JOIN `tbl_RACF_Gruppen` ON
                    (
                        (
                            `tbl_RACF_Gruppen`.`Group` = `tblGesamt`.`TF`
                        )
                    )
                )
            LEFT JOIN `tblOrga` ON
                (
                    (
                        `tblOrga`.`ID` = `tblUserIDundName`.`Orga_ID`
                    )
                )
            )
        ON
            (
                (
                    `tblPlattform`.`ID` = `tblGesamt`.`Plattform_ID`
                )
            )
        )
    ON
        (
            (
                `tblÜbersichtAF_GFs`.`ID` = `tblGesamt`.`Modell`
            )
        )
    )
    where
  	 `ZI-organisation` = 'AI-BA'
     	AND NOT `tblGesamt`.`gelöscht`
        AND NOT `tblUserIDundName`.`gelöscht`
	LIMIT 3





SELECT COUNT (`tblGesamt``.`id``)
FROM
    (
        `tblÜbersichtAF_GFs`
    JOIN(
            `tblPlattform`
        JOIN(
                (
                    (
                        `tblUserIDundName`
                    JOIN `tblGesamt` ON
                        (
                            (
                                (`tblUserIDundName`.`gelöscht` <> 1) AND(
                                    `tblUserIDundName`.`ID` = `tblGesamt`.`UserID + Name_ID`
                                )
                            )
                        )
                    )
                LEFT JOIN `tbl_RACF_Gruppen` ON
                    (
                        (
                            `tbl_RACF_Gruppen`.`Group` = `tblGesamt`.`TF`
                        )
                    )
                )
            LEFT JOIN `tblOrga` ON
                (
                    (
                        `tblOrga`.`ID` = `tblUserIDundName`.`Orga_ID`
                    )
                )
            )
        ON
            (
                (
                    `tblPlattform`.`ID` = `tblGesamt`.`Plattform_ID`
                )
            )
        )
    ON
        (
            (
                `tblÜbersichtAF_GFs`.`ID` = `tblGesamt`.`Modell`
            )
        )
    )
    where
  	 `ZI-organisation` = 'AI-BA'
     	AND NOT `tblGesamt`.`gelöscht`
        AND NOT `tblUserIDundName`.`gelöscht`


SET global general_log = 1;
SET global log_output = 'table';
SET global general_log = 0;

SELECT * FROM `mysql`.`general_log` WHERE event_time  > (now() - INTERVAL 8 SECOND) AND `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC
SELECT * FROM `mysql`.`general_log` WHERE `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC





class VwMehrfach(models.Model):
	id = 					models.IntegerField(db_column='ID', primary_key=True)
	userid = 				models.CharField(db_column='UserID', max_length=50)  # Field name made lowercase.
	name = 					models.CharField(db_column='Name', max_length=150, blank=True, null=True)  # Field name made lowercase.
	gruppe = 				models.CharField(max_length=50, blank=True, null=True)
	team = 					models.CharField(max_length=50, blank=True, null=True)
	tf = 					models.CharField(db_column='TF', max_length=150)  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='TF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='Enthalten IN AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	afneu = 				models.CharField(max_length=50)
	gfneu = 				models.CharField(max_length=50, blank=True, null=True)
	plattform = 			models.CharField(max_length=150, blank=True, null=True)
	gf = 					models.CharField(db_column='GF', max_length=150, blank=True, null=True)  # Field name made lowercase.
	gf_beschreibung = 		models.CharField(db_column='GF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	orga_id = 				models.IntegerField(db_column='Orga_ID')  # Field name made lowercase.
	useridundname_id = 		models.IntegerField(db_column='UserIDundName_ID', blank=True, null=True)  # Field name made lowercase.
	modell = 				models.IntegerField(db_column='Modell')  # Field name made lowercase.
	plattform_id = 			models.IntegerField(db_column='Plattform_ID', blank=True, null=True)  # Field name made lowercase.
	geloescht = 			models.IntegerField(blank=True, null=True)
	loeschdatum = 			models.DateTimeField(blank=True, null=True)
	af_gueltig_ab = 		models.DateTimeField(db_column='AF Gueltig ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='AF Gueltig bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='Direct Connect', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = \
							models.CharField(db_column='Hoechste Kritikalitaet TF IN AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = 	models.DateTimeField(db_column='AF Zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	test = 					models.TextField(db_column='Test', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
	produktion = 			models.TextField(db_column='Produktion', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
	readonly = 				models.TextField(db_column='Readonly', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
	tf_kritikalitaet = 		models.CharField(db_column='TF_Kritikalitaet', max_length=150, blank=True, null=True)  # Field name made lowercase.
	tf_eigentuemer_org = 	models.CharField(db_column='TF_Eigentuemer Org', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zi_organisation = 		models.CharField(db_column='ZI_Organisation', max_length=50, blank=True, null=True)  # Field name made lowercase.
	vip = 					models.CharField(db_column='VIP', max_length=150, blank=True, null=True)  # Field name made lowercase.
	zufallsgenerator = 		models.CharField(db_column='Zufallsgenerator', max_length=150, blank=True, null=True)  # Field name made lowercase.
	datum = 				models.DateTimeField(db_column='Datum')  # Field name made lowercase.
	gefunden = 				models.IntegerField(blank=True, null=True)
	wiedergefunden = 		models.DateTimeField(blank=True, null=True)
	geaendert = 			models.TextField(blank=True, null=True)  # This field type is a guess.
	neueaf = 				models.CharField(db_column='NeueAF', max_length=50, blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'vw_mehrfach'
		verbose_name = "Selektierte Zeile"
		verbose_name_plural = "Selektierte Menge"
		# ordering = ['userid_name']

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

	def get_absolute_url(self):
		# Returns the url to access a particular instance of the model.
		return reverse('mehrfach-detail', args=[str(self.id)])


-- Löschen von Einträgen ind er RechteDB, bei denen die User bereits belöscht wurden (ca. 900 Stück)

CREATE TEMPORARY TABLE test (
    select `tblGesamt`.`id`
    FROM `tblGesamt`
        INNER JOIN `tblUserIDundName`
        ON (
            `tblGesamt`.`gelöscht` = 0 and
            `tblGesamt`.`UserID + Name_ID` = `tblUserIDundName`.`ID`
            and `tblUserIDundName`.`gelöscht` = 1
            and `tblUserIDundName`.`userid` = 'AV93323'
        )
);

select * from test;

SELECT `tblGesamt`.*
    from `tblGesamt`
        INNER JOIN `test`
        ON (`tblGesamt`.`ID` = `test`.`ID`);

Select count(*) FROM `tblGesamt` ges
    INNER JOIN `test`
    ON (`ges`.`ID` = `test`.`id`);

UPDATE `tblGesamt` ges
    INNER JOIN `test`
    ON (`ges`.`ID` = `test`.`id` and `test`.`id` = '1')
    SET `ges`.`gelöscht` = '1';


# SQLs zum Umsetzen der Indizes von direktem Feld auf die korrekte ID

SELECT `tbl_RolleHatAFNeu`.`RollenMappingID`, `tbl_RolleHatAFNeu`.`RollenName`, `tbl_RolleHatAFNeu`.`AF`, `tbl_RolleHatAFNeu`.`AFName`,
		`tbl_AFListe`.`ID`, `tbl_AFListe`.`AF-Name`, `tbl_AFListe`.`neu ab`
FROM `tbl_RolleHatAFNeu`
	join `tbl_AFListe`
    on (`tbl_RolleHatAFNeu`.`AFName` = `tbl_AFListe`.`AF-Name`)

    Where `RollenName` LIKE '%Produktionsvorbereitung Leitung%'


update `tbl_RolleHatAFNeu` raf
	inner join `tbl_AFListe`
    on (raf.`AFName` = `tbl_AFListe`.`AF-Name`)
    set raf.`AF` = `tbl_AFListe`.`ID`

