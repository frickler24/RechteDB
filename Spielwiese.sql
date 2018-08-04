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

SELECT `tbl_RolleHatAF`.`RollenMappingID`, `tbl_RolleHatAF`.`RollenName`, `tbl_RolleHatAF`.`AF`, `tbl_RolleHatAF`.`AFName`,
		`tbl_AFListe`.`ID`, `tbl_AFListe`.`AF-Name`, `tbl_AFListe`.`neu ab`
FROM `tbl_RolleHatAF`
	join `tbl_AFListe`
    on (`tbl_RolleHatAF`.`AFName` = `tbl_AFListe`.`AF-Name`)

    Where `RollenName` LIKE '%Produktionsvorbereitung Leitung%'


update `tbl_RolleHatAF` raf
	inner join `tbl_AFListe`
    on (raf.`AFName` = `tbl_AFListe`.`AF-Name`)
    set raf.`AF` = `tbl_AFListe`.`ID`


-- Manueller Import einer neuen Liste in die Datenbank

/*
    Einlesen einer Datei über einen gespeicherten Import.Es wird die Datei gelesen,
    die im Import "User und TF komplett Neu für Import per Macro" steht.
    Standardmäßig heißt die Datei "&lt;absoluter Pfad&gt;\User und TF komplett Neu.xlsx"
    und enthält als erstes ein Datenblatt mit Namen "Sheet1",
    das genau der Exportstruktur von NIBA entspricht.
    Die Daten werden zunächst in eine Hilfstabelle tblRechteNeuVonImport eingelesen
    und dann von dort in die vorher geleerte tblRechteAMNeu kopiert.
    tblRechteAMNeu ist ab dann die Arbeitsdatei für alle weiteren Vorgänge,
    die Hilfsdatei wird nicht mehr benutzt.Dieser Zwischenschritt war früher erforderlich,
    weil der gespeicherte Import die Tabelle komplett gelöscht hat
    (also eine DROP - CREATE - Sequenz durchlief),
    damit waren die Datentypangaben und Referenzen futsch.
    Heute wird enur noch genutzt, um die doppelt eingelesenen Zeilen zu entfernen
    und dynamische Werte zu erzeugen.
*/

TRUNCATE `tblRechteNeuVonImport`;
LOAD DATA LOCAL INFILE '/tmp/phpbojCHf'     -- ACHTUNGG ToDO Die Daten wirklich vom File einlesen
    REPLACE INTO TABLE `tblRechteNeuVonImport`
    FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\' LINES TERMINATED BY '\n';

/*
-- Nur zur Sicherheit vorher mal gucken
SELECT count(*) FROM `tblRechteNeuVonImport`
WHERE (((tblRechteNeuVonImport.`AF zugewiesen an Account-Name`) Is Null
    Or (tblRechteNeuVonImport.`AF zugewiesen an Account-Name`)=""));
*/
/*
    Seit IIQ werden die wirklichen UserIDen nicht mehr unter der Identität gehalten,
    sondern unter `AF zugewiesen an Account-Name`. Das müssen wir in die UserID
    umkopieren, wo nötig.
*/
UPDATE tblRechteNeuVonImport
    SET `AF zugewiesen an Account-Name` = `Identität`
WHERE (((tblRechteNeuVonImport.`AF zugewiesen an Account-Name`) Is Null
    Or (tblRechteNeuVonImport.`AF zugewiesen an Account-Name`)=""));

/*
    Da hat es wohl mal Irritationen mit UserIDen gegeben:
    Technische User wurden mit anderen UserIDen angezeigt, als XV86-er Nummern
    Das wird hier korrigiert.
*/


UPDATE tblRechteNeuVonImport
	SET tblRechteNeuVonImport.`AF zugewiesen an Account-Name` = `Identität`
WHERE tblRechteNeuVonImport.`Identität` Like 'xv86%'
    AND tblRechteNeuVonImport.`AF zugewiesen an Account-Name` Not Like 'xv86%';

/*
    zum Nachschauen

select `Identität`, `AF zugewiesen an Account-Name` from tblRechteNeuVonImport
WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-Name` Not Like 'xv86%'
	AND `tblRechteNeuVonImport`.`Identität` Like 'xv86%';
*/

/*
    Leeren und Füllen der eigentlichen Importtabelle
    Einschließlich Herausfiltern der doppelten Zeilen
    (> 1% der Zeilen werden aus IIQ doppelt geliefert)
*/
truncate tblRechteAMNeu;

CREATE TEMPORARY TABLE qryF3_RechteNeuVonImportDuplikatfrei (
    SELECT /*tblRechteNeuVonImport.ID,*/
           tblRechteNeuVonImport.`AF zugewiesen an Account-Name` AS UserID,
           CONCAT(`Nachname`,', ',`Vorname`) AS Name,
           tblRechteNeuVonImport.`TF Name` AS TF,
           tblRechteNeuVonImport.`TF Beschreibung`,
           tblRechteNeuVonImport.`AF Anzeigename` AS `Enthalten in AF`,
           tblRechteNeuVonImport.`TF Kritikalität`,
           tblRechteNeuVonImport.`TF Eigentümer Org`,
           tblRechteNeuVonImport.`TF Applikation` AS `TF Technische Plattform`,
           tblRechteNeuVonImport.`GF Name` AS GF,
           'gibt es nicht mehr' AS `VIP Kennzeichen`,
           'gibt es nicht mehr' AS Zufallsgenerator,
           tblRechteNeuVonImport.`AF Gültig ab`,
           tblRechteNeuVonImport.`AF Gültig bis`,
           tblRechteNeuVonImport.`Direct Connect`,
           tblRechteNeuVonImport.`Höchste Kritikalität TF in AF`,
           tblRechteNeuVonImport.`GF Beschreibung`,
           tblRechteNeuVonImport.`AF Zuweisungsdatum`
    FROM tblRechteNeuVonImport
    GROUP BY
             tblRechteNeuVonImport.`AF zugewiesen an Account-Name`,
             tblRechteNeuVonImport.`TF Name`,
             tblRechteNeuVonImport.`AF Anzeigename`,
             tblRechteNeuVonImport.`TF Applikation`,
             tblRechteNeuVonImport.`GF Name`
);

INSERT INTO tblRechteAMNeu (UserID, Name, TF, `TF Beschreibung`, `Enthalten in AF`, `TF Kritikalität`,
            `TF Eigentümer Org`, `TF Technische Plattform`, GF, `VIP Kennzeichen`, Zufallsgenerator, 
            `AF Gültig ab`, `AF Gültig bis`, `Direct Connect`, `Höchste Kritikalität TF in AF`, 
            `GF Beschreibung`, `AF Zuweisungsdatum`)
SELECT qryF3_RechteNeuVonImportDuplikatfrei.UserID,
       qryF3_RechteNeuVonImportDuplikatfrei.Name,
       qryF3_RechteNeuVonImportDuplikatfrei.TF,
       qryF3_RechteNeuVonImportDuplikatfrei.`TF Beschreibung`,
       qryF3_RechteNeuVonImportDuplikatfrei.`Enthalten in AF`,
       qryF3_RechteNeuVonImportDuplikatfrei.`TF Kritikalität`,
       qryF3_RechteNeuVonImportDuplikatfrei.`TF Eigentümer Org`,
       qryF3_RechteNeuVonImportDuplikatfrei.`TF Technische Plattform`,
       qryF3_RechteNeuVonImportDuplikatfrei.GF,
       qryF3_RechteNeuVonImportDuplikatfrei.`VIP Kennzeichen`,
       qryF3_RechteNeuVonImportDuplikatfrei.Zufallsgenerator,
       qryF3_RechteNeuVonImportDuplikatfrei.`AF Gültig ab`,
       qryF3_RechteNeuVonImportDuplikatfrei.`AF Gültig bis`,
       qryF3_RechteNeuVonImportDuplikatfrei.`Direct Connect`,
       qryF3_RechteNeuVonImportDuplikatfrei.`Höchste Kritikalität TF in AF`,
       qryF3_RechteNeuVonImportDuplikatfrei.`GF Beschreibung`,
       qryF3_RechteNeuVonImportDuplikatfrei.`AF Zuweisungsdatum`
FROM qryF3_RechteNeuVonImportDuplikatfrei;

/*
    Beim Kopieren ist wichtig, dass die Felder,
    die später in JOINs verwendet werden sollen,
    keine NULL-Werte enthalten.
    Das wird durch die nachfolgenden simplen Korrektur-SQLs sichergestellt.
*/
UPDATE tblRechteAMNeu SET `TF Beschreibung` = 'ka' WHERE `TF Beschreibung` Is Null Or `TF Beschreibung` = '';
UPDATE tblRechteAMNeu SET `Enthalten in AF` = 'ka' WHERE `Enthalten in AF` Is Null or `Enthalten in AF`  ='';
UPDATE tblRechteAMNeu SET `TF` = 'Kein Name' WHERE `TF` Is Null or `TF`  = '';
UPDATE tblRechteAMNeu SET `TF Technische Plattform` = 'Kein Name' WHERE `TF Technische Plattform` Is Null or `TF Technische Plattform`  = '';
UPDATE tblRechteAMNeu SET `TF Kritikalität` = 'ka' WHERE `TF Kritikalität` Is Null or  `TF Kritikalität` = '';
UPDATE tblRechteAMNeu SET `TF Eigentümer Org` = 'ka' WHERE `TF Eigentümer Org` Is Null or  `TF Eigentümer Org` = '';
UPDATE tblRechteAMNeu SET `GF` = 'k.A.' WHERE GF Is Null or GF = '';
UPDATE tblRechteAMNeu SET `VIP Kennzeichen` = 'k.A.' WHERE `VIP Kennzeichen` Is Null or  `VIP Kennzeichen` = '';
UPDATE tblRechteAMNeu SET `Zufallsgenerator` = 'k.A.' WHERE `Zufallsgenerator` Is Null or `Zufallsgenerator` = '';
 
/*
-- Sollte nun 0 ergeben:
select count(*) from tblRechteAMNeu 
    WHERE `TF Beschreibung` Is Null Or `TF Beschreibung` = ''
    or `Enthalten in AF` Is Null or `Enthalten in AF`  = ''
    or `TF` Is Null or `TF`  = ''
    or `TF Technische Plattform` Is Null or `TF Technische Plattform`  = ''
    or `TF Kritikalität` Is Null or  `TF Kritikalität` = ''
    or `TF Eigentümer Org` Is Null or  `TF Eigentümer Org` = ''
    or GF Is Null or GF = ''
    or `VIP Kennzeichen` Is Null or  `VIP Kennzeichen` = ''
    or `Zufallsgenerator` Is Null or `Zufallsgenerator` = '';
*/

/*
    Erzeuge die Liste der erlaubten Arbeitsplatzfunktionen.
    Sei wird später in der Rollenbehandlung benötigt.
*/
INSERT INTO tbl_AFListe ( `AF-Name` )
    SELECT `tblÜbersichtAF_GFs`.`Name AF Neu`
        FROM tblÜbersichtAF_GFs LEFT JOIN tbl_AFListe ON tblÜbersichtAF_GFs.`Name AF Neu` = tbl_AFListe.`AF-Name`
        WHERE (((tblÜbersichtAF_GFs.modelliert) Is Not Null) AND ((tbl_AFListe.`AF-Name`) Is Null))
    GROUP BY tblÜbersichtAF_GFs.`Name AF Neu`;

SYNTAX-FEHLER!!!!! Dient dazu, dass hier erst mal angehalten wird

/*
    Bis hierhin ging die Vorbereitung.
    Die nächsten Schritte müssen manuell und visuell unterstützt werden:
        - Sichtung der neu hinzugekommenen UserIDen,
        - Übernahme in die UserID-Liste
        - Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf gelöscht werden sollen
*/
/*
    Zunächst die Suche nach neu hinzugekommenen Usern:
*/

SELECT DISTINCT tblRechteAMNeu.UserID,
                tblRechteAMNeu.Name,
                '35' AS Ausdr1,
                'AI-BA' AS Ausdr2,
                tblUserIDundName.UserID,
                tblUserIDundName.Name,
                tblUserIDundName.gelöscht
FROM tblUserIDundName
RIGHT JOIN tblRechteAMNeu ON (tblUserIDundName.UserID = tblRechteAMNeu.UserID)
AND (tblUserIDundName.Name = tblRechteAMNeu.Name)
WHERE (((tblRechteAMNeu.UserID) IS NOT NULL)
       AND ((tblUserIDundName.UserID) IS NULL))
  OR (((tblRechteAMNeu.Name) IS NOT NULL)
      AND ((tblUserIDundName.Name) IS NULL))
  OR (((tblUserIDundName.gelöscht)=TRUE));

/*
    Dieses Makro wird aufgerufen, wenn der "Neue User speichern" Button angeklickt wird.
    Zunächst werden die User in eine temporäre Tabelle geschrieben,
    um sie entweder in der vorhandenen User-Tabelle, in der auf "gelöscht" gesetzt sind,
    wieder zu reaktivieren, oder sie werden an die vorhandene User-Tabelle angehängt.
*/

create temporary table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a as
    SELECT DISTINCT tblRechteAMNeu.UserID as UserID1,
            tblRechteAMNeu.Name as Name1,
            '35' AS Ausdr1,
            'AI-BA' AS Ausdr2,
            tblUserIDundName.UserID as UserID2,
            tblUserIDundName.Name as Name2,
            tblUserIDundName.gelöscht
    FROM tblUserIDundName
    RIGHT JOIN tblRechteAMNeu ON (tblUserIDundName.UserID = tblRechteAMNeu.UserID)
    AND (tblUserIDundName.Name = tblRechteAMNeu.Name)
    WHERE (((tblRechteAMNeu.UserID) IS NOT NULL)
           AND ((tblUserIDundName.UserID) IS NULL))
      OR (((tblRechteAMNeu.Name) IS NOT NULL)
          AND ((tblUserIDundName.Name) IS NULL))
      OR (((tblUserIDundName.gelöscht)=TRUE));


create temporary table tbl_tmpGeloeschte as
    SELECT qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a.UserID1
    FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
    WHERE qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a.gelöscht =True;

select * from tbl_tmpGeloeschte;
-- select * from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;

/*
    Markiere die UserIDen, die bereits bekannt, aber als gelöscht markiert sind,
    wieder als aktiv.
*/
UPDATE tbl_tmpGeloeschte
    INNER JOIN tblUserIDundName
    ON tbl_tmpGeloeschte.UserID1 = tblUserIDundName.UserID
SET tblUserIDundName.gelöscht = False;

/*
    Nun werden die wirklich neuen User an die UserID-Tabelle angehängt
*/

create temporary table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2 as
    SELECT UserID1, Name1, Ausdr1, Ausdr2, gelöscht
    FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
    WHERE (`gelöscht` = FALSE or `gelöscht` IS NULL)
    AND (UserID1 IS NOT NULL OR Name1 IS NOT NULL);

INSERT INTO tblUserIDundName (UserID, Name, Orga_ID, `ZI-Organisation` )
SELECT  UserID1,
        Name1,
        Ausdr1 AS Orga_ID,
        Ausdr2 AS `ZI-Organisation`
        FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2;

select * from tblUserIDundName;


SYNTAX-FEHLER!!!!! Dient dazu, dass hier erst mal angehalten wird. Es müssen die Einträge der neuen und geänderten User ergänzt / korrigiert werden.

/*
    Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf gelöscht werden sollen
    Erst einmal werden die Rechte der al zu löschen markierten User in die Historientabelle verschoben.
*/


create temporary table qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a as
SELECT A.UserID, A.Name, A.`ZI-Organisation`
    FROM tblUserIDundName A
    WHERE   A.`ZI-Organisation` = 'ai-ba'
        AND A.gelöscht = FALSE
        AND A.UserID not in (select distinct userid from tblRechteAMNeu)
    GROUP BY
        A.UserID,
        A.Name,
        A.`ZI-Organisation`
;

-- SELECT * from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;

INSERT INTO tblGesamtHistorie (
            `UserID + Name_ID`, TF, `TF Beschreibung`, `Enthalten in AF`, Modell, `TF Kritikalität`, `TF Eigentümer Org`,
            Plattform_ID, gelöscht, gefunden, wiedergefunden, geändert, löschdatum, NeueAF, Datum, `ID-alt`
        )
SELECT `tblGesamt`.`UserID + Name_ID`,
       `tblGesamt`.TF,
       `tblGesamt`.`TF Beschreibung`,
       `tblGesamt`.`Enthalten in AF`,
       `tblGesamt`.Modell,
       `tblGesamt`.`TF Kritikalität`,
       `tblGesamt`.`TF Eigentümer Org`,
       `tblGesamt`.Plattform_ID,
       `tblGesamt`.`gelöscht`,
       `tblGesamt`.gefunden,
       `tblGesamt`.wiedergefunden,
       `tblGesamt`.`geändert`,
       Now() AS Ausdr1,
       `tblGesamt`.NeueAF,
       `tblGesamt`.Datum,
       `tblGesamt`.ID
FROM tblUserIDundName
INNER JOIN `tblGesamt` ON tblUserIDundName.ID = `tblGesamt`.`UserID + Name_ID`
WHERE (((tblUserIDundName.UserID) IN
          (SELECT UserID
           FROM `qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a`))
       AND ((tblUserIDundName.gelöscht)=FALSE));

-- Nun Setzen der Löschflags in der Gesamttabelle für jedes Recht jeder nicht mehr vorhandenen UserID

UPDATE
    tblGesamt
    INNER JOIN tblUserIDundName
    ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
SET tblGesamt.gelöscht = TRUE,
    tblGesamt.löschdatum = Now()
WHERE tblGesamt.`gelöscht` = FALSE
    AND tblUserIDundName.`gelöscht` = FALSE
    AND tblUserIDundName.UserID IN (SELECT UserID FROM `qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a`);

-- Die User werden in der User-Tabelle nun auf "gelöscht" gesetzt

UPDATE tblUserIDundName
SET `gelöscht` = TRUE
WHERE `gelöscht` = FALSE
    AND UserID IN (SELECT UserID FROM `qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a`);

-- ToDo Es fehlt komplett das Auslagern der historisierten Rechte

/*
    Nun folgt der komplexere Block:
    Die neuen, evtl. unveränderten und auch nicht mehr vorhandenen einzelnen Berechtigungen
    müssen schrittweise in die Gesamttabelle eingetragen werden.
*/

-- Lösche zunächst Plattform-Namen, die in der Gesamttabelle nicht mehr auftauchen
-- (manchmal werden Plattformn einfach umbenannt)
CREATE TEMPORARY TABLE bloed as
    SELECT tblPlattform.`TF Technische Plattform` as x
        FROM tblPlattform
        LEFT JOIN tblGesamt ON tblPlattform.ID = tblGesamt.Plattform_ID
        WHERE tblGesamt.Plattform_ID IS NULL;
DELETE FROM tblPlattform
WHERE `TF Technische Plattform` IN (select x from bloed);

-- Ergänze alle Plattformen, die bislang nur in tblRechteAMNeu bekannt sind
INSERT INTO tblPlattform (`TF Technische Plattform`)
SELECT DISTINCT tblRechteAMNeu.`TF Technische Plattform`
FROM tblRechteAMNeu
    LEFT JOIN tblPlattform
    ON tblRechteAMNeu.`TF Technische Plattform` = tblPlattform.`TF Technische Plattform`
WHERE tblPlattform.`TF Technische Plattform` IS NULL;

/*
    Der Status "gefunden" dient dazu,
    später die Selektion neuer Rechte zu vereinfachen und übriggebliebene Rechte zu löschen.
    Er wird sowohl in der Gesamt-Tabelle, als auch in der Importtabelle zurückgesetzt.
    Gleichzeitig wird der Status "geändert" in beiden Tabellen zurückgesetzt.
*/

UPDATE tblUserIDundName
    INNER JOIN tblGesamt
    ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`
SET tblGesamt.gefunden = FALSE,
    tblGesamt.geändert = FALSE
WHERE tblGesamt.gefunden = TRUE OR tblGesamt.`geändert` = TRUE;

-- Dies hier nur zur Sicherheit - eigentlich müssten die eh null sein
UPDATE tblRechteAMNeu
SET tblRechteAMNeu.Gefunden = FALSE,
    tblRechteAMNeu.Geändert = FALSE
WHERE tblRechteAMNeu.Gefunden = TRUE
    OR tblRechteAMNeu.Geändert = TRUE;

/*
    Nun wird die "flache" Tabelle "tbl_Gesamt_komplett" erzeugt.
    Dort sind die Referenzen zu den User- und Berechtigungs- und Orga-Tabellen aufgelöst,
    allerdings in dieser Implementierung aussschliußlich für die benötigten UserIDen
    (früher wirklich komplett).

    ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller UserIDs benötigt wird
*/

drop table if exists tbl_Gesamt_komplett;
create temporary table tbl_Gesamt_komplett as
    SELECT tblGesamt.ID,
           tblUserIDundName.UserID,
           tblUserIDundName.Name,
           tblGesamt.TF,
           tblGesamt.`TF Beschreibung`,
           tblGesamt.`Enthalten in AF`,
           tblÜbersichtAF_GFs.`Name GF Neu`,
           tblÜbersichtAF_GFs.`Name AF Neu`,
           tblGesamt.`TF Kritikalität`,
           tblGesamt.`TF Eigentümer Org`,
           tblPlattform.`TF Technische Plattform`,
           tblGesamt.GF,
           tblGesamt.`VIP Kennzeichen`,
           tblGesamt.Zufallsgenerator,
           tblGesamt.Modell,
           tblUserIDundName.Orga_ID,
           tblUserIDundName.`ZI-Organisation`,
           tblGesamt.`AF Gültig ab`,
           tblGesamt.`AF Gültig bis`,
           tblGesamt.`Direct Connect`,
           tblGesamt.`Höchste Kritikalität TF in AF`,
           tblGesamt.`GF Beschreibung`,
           tblGesamt.`AF Zuweisungsdatum`,
           tblGesamt.Datum,
           tblGesamt.`gelöscht`
    FROM tblGesamt
        INNER JOIN tblÜbersichtAF_GFs
        ON tblGesamt.Modell = tblÜbersichtAF_GFs.ID

        INNER JOIN tblPlattform
        ON tblPlattform.ID = tblGesamt.Plattform_ID

        INNER JOIN tblUserIDundName
        ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID

    WHERE tblGesamt.`gelöscht` = FALSE
        AND tblUserIDundName.UserID in (select distinct userid from tblRechteAMNeu)
    ORDER BY tblGesamt.TF,
             tblUserIDundName.UserID;

/*
    Markieren der Flag Gefunden in tblRechteAMNeu sowie tblGesamt.
    In letzterer wird auch das DFatum eingetragen wann das Recht wiedergefunden wurde.

    Zusätzlich werden alle Felder, die hier nicht zum Vergleich der Rechte-Gleichheit
    genutzt wurden, in der Gesamttabelle aktualisiert.

    Das hat früher mal zu Problöemen geführt, in letzter Zeit aber eher nicht mehr.

*/

UPDATE tblRechteAMNeu
    INNER JOIN tblGesamt
    ON      tblRechteAMNeu.TF = tblGesamt.TF
        AND tblRechteAMNeu.GF = tblGesamt.GF
        AND tblRechteAMNeu.`Enthalten in AF` = tblGesamt.`Enthalten in AF`
        AND tblRechteAMNeu.Zufallsgenerator = tblGesamt.Zufallsgenerator
        AND tblRechteAMNeu.`VIP Kennzeichen` = tblGesamt.`VIP Kennzeichen`

    INNER JOIN tblUserIDundName
    ON      tblUserIDundName.UserID = tblRechteAMNeu.UserID
        AND tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

    INNER JOIN tblPlattform
    ON      tblPlattform.`TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`
        AND tblPlattform.ID = tblGesamt.Plattform_ID

SET tblGesamt.gefunden = TRUE,
    tblGesamt.Wiedergefunden = Now(),
    tblRechteAMNeu.Gefunden = TRUE,
    tblGesamt.`TF Beschreibung` = `tblRechteAMNeu`.`TF Beschreibung`,
    tblGesamt.`TF Kritikalität` = `tblRechteAMNeu`.`TF Kritikalität`,
    tblGesamt.`TF Eigentümer Org` = `tblRechteAMNeu`.`TF Eigentümer Org`,
    tblGesamt.`AF Gültig ab` = `tblRechteAMNeu`.`AF Gültig ab`,
    tblGesamt.`AF Gültig bis` = `tblRechteAMNeu`.`AF Gültig bis`,
    tblGesamt.`Direct Connect` = `tblRechteAMNeu`.`Direct Connect`,
    tblGesamt.`Höchste Kritikalität TF in AF` = `tblRechteAMNeu`.`Höchste Kritikalität TF in AF`,
    tblGesamt.`GF Beschreibung` = `tblRechteAMNeu`.`GF Beschreibung`,
    tblGesamt.`AF Zuweisungsdatum` = `tblRechteAMNeu`.`AF Zuweisungsdatum`

WHERE tblGesamt.`gelöscht`= FALSE
    AND tblUserIDundName.`gelöscht`= FALSE;


/*
    Dasselbe, nur zum Lesen.
    Falls mal wieder ein Unglück mit den VIPs oder dem Zufallsgenertator passieren sollte...
* /
SELECT * FROM tblRechteAMNeu
    INNER JOIN tblGesamt
    ON      tblRechteAMNeu.TF = tblGesamt.TF
        AND tblRechteAMNeu.GF = tblGesamt.GF
        AND tblRechteAMNeu.`Enthalten in AF` = tblGesamt.`Enthalten in AF`
        AND tblRechteAMNeu.Zufallsgenerator = tblGesamt.Zufallsgenerator
        AND tblRechteAMNeu.`VIP Kennzeichen` = tblGesamt.`VIP Kennzeichen`

    INNER JOIN tblUserIDundName
    ON      tblUserIDundName.UserID = tblRechteAMNeu.UserID
        AND tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

    INNER JOIN tblPlattform
    ON      tblPlattform.`TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`
        AND tblPlattform.ID = tblGesamt.Plattform_ID

WHERE
    tblUserIDundName.`gelöscht`= FALSE
        AND tblGesamt.`gelöscht`= FALSE
;

*/

/*
    qryF2setzeGeaentderteAlteAF
*/

UPDATE tblRechteAMNeu
    INNER JOIN tblGesamt
    ON      tblRechteAMNeu.TF = tblGesamt.TF
        AND tblRechteAMNeu.GF = tblGesamt.GF
        AND tblRechteAMNeu.Zufallsgenerator = tblGesamt.Zufallsgenerator
        AND tblRechteAMNeu.`VIP Kennzeichen` = tblGesamt.`VIP Kennzeichen`

    INNER JOIN tblUserIDundName
    ON      tblUserIDundName.UserID = tblRechteAMNeu.UserID
        AND tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

    INNER JOIN tblPlattform
    ON      tblPlattform.`TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`
        AND tblPlattform.ID = tblGesamt.Plattform_ID

SET tblGesamt.geändert = TRUE,
    tblRechteAMNeu.Geändert = TRUE,
    tblGesamt.NeueAF = `tblRechteAMNeu`.`Enthalten in AF`

WHERE   tblGesamt.`Enthalten in AF` <> tblRechteAMNeu.`Enthalten in AF`
    AND tblGesamt.gefunden = FALSE
    AND tblRechteAMNeu.Gefunden = FALSE
    AND tblUserIDundName.`gelöscht` = FALSE
    AND tblGesamt.`gelöscht` = FALSE
    ;

/*
    Und wieder mal zum Gucken
* /
select * from tblRechteAMNeu
    INNER JOIN tblGesamt
    ON      tblRechteAMNeu.TF = tblGesamt.TF
        AND tblRechteAMNeu.GF = tblGesamt.GF
        AND tblRechteAMNeu.Zufallsgenerator = tblGesamt.Zufallsgenerator
        AND tblRechteAMNeu.`VIP Kennzeichen` = tblGesamt.`VIP Kennzeichen`

    INNER JOIN tblUserIDundName
    ON      tblUserIDundName.UserID = tblRechteAMNeu.UserID
        AND tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

    INNER JOIN tblPlattform
    ON      tblPlattform.`TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`
        AND tblPlattform.ID = tblGesamt.Plattform_ID

WHERE   tblGesamt.`Enthalten in AF` <> tblRechteAMNeu.`Enthalten in AF`
    AND tblGesamt.gefunden = FALSE
    AND tblRechteAMNeu.Gefunden = FALSE
    AND tblUserIDundName.`gelöscht` = FALSE
    AND tblGesamt.`gelöscht` = FALSE

*/

/*
    qryF5c_HistorisiereGeaenderteEintraege
    In die Historientabelle werden die zur Änderung vorgemerkten Einträge aus der Gesamttabelle kopiert.
*/

INSERT INTO tblGesamtHistorie (`UserID + Name_ID`, TF, `TF Beschreibung`, `Enthalten in AF`, Modell, `TF Kritikalität`,
            `TF Eigentümer Org`, Plattform_ID, GF, `VIP Kennzeichen`, Zufallsgenerator, gelöscht, gefunden,
            wiedergefunden, geändert, NeueAF, Datum, `ID-alt`, löschdatum)
SELECT tblGesamt.`UserID + Name_ID`,
       tblGesamt.TF,
       tblGesamt.`TF Beschreibung`,
       tblGesamt.`Enthalten in AF`,
       tblGesamt.Modell,
       tblGesamt.`TF Kritikalität`,
       tblGesamt.`TF Eigentümer Org`,
       tblGesamt.Plattform_ID,
       tblGesamt.GF,
       tblGesamt.`VIP Kennzeichen`,
       tblGesamt.Zufallsgenerator,
       tblGesamt.gelöscht,
       tblGesamt.gefunden,
       Now() AS Ausdr1,
       tblGesamt.geändert,
       tblGesamt.NeueAF,
       tblGesamt.Datum,
       tblGesamt.ID,
       tblGesamt.löschdatum
FROM tblUserIDundName
    INNER JOIN tblGesamt
    ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

WHERE tblGesamt.`geändert` = TRUE
       AND tblUserIDundName.`ZI-Organisation` LIKE 'AI-BA';      -- ToDo: Wird die EInschränkung wirklich benötigt?


/*
    Anschließend können die geänderten Werte in die GesamtTabelle übernommen werden.
    Dazu wird der Inhalt des Kommentarfelds in die AF-alt-Spalte eingetragen.
    Damit müsste das erledigt sein :-)

    qryF5d_AktualisiereGeaenderteAF
*/

UPDATE tblUserIDundName
    INNER JOIN tblGesamt
    ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`
SET tblGesamt.`Enthalten in AF` = `NeueAF`

WHERE tblGesamt.`geändert` = TRUE
    AND tblUserIDundName.`ZI-Organisation` = 'AI-BA';

-- ToDo: Später noch mal das geändert-Flag zurücksetzen, dann entfällt das ToDo vorher...






















<Comment>Als nächstes kann es sein, dass in der Importliste noch TF mit NEUEN AF stehen, die zwar bereits in der Gesamtliste bezogen auf die UID bekannt sind, dort aber bereits mit den ALTEN AF-Bezeichnungen gefunden wurden. Damit nun nicht bei jedem wiederholten Import die AF-Bezeichnungen umgeschossen werden, hängen wir diese Zeilen nun hinten an die Gesamttabelle an.</Comment>
<Comment>Dazu werden im ersten Schritt in der Importtabelle die Zeilen markiert (angehaengtBekannt), die anzuhängen sind. Das sieht zwar umständlich aus, erleichtert aber später die Bewertung. ob noch irgendwelche Einträge in der Importtabelle nicht bearbeitet wurden. Die Flags kann man eigentlich auch zusammenfassen, dann müssten aber bearbeitete Zeilen separat umgeschossen werden...</Comment>
<Comment>Beim Einfügen der neuen TF-AF-Kombinationen wird in der Gesamttabelle das Flag "gefunden" gesetzt, damit es später icht gleich wieder gelöscht wird.</Comment>
    <Argument Name="QueryName">qryF5_FlaggeTFmitNeuenAFinImportTabelle</Argument>
<Comment>Anschließend werden diese selektierten Zeilen an die Gesamttabelle angehängt. Dabei wird in der Gesamttabelle das Flag "gefunden" gesetzt, um diese Einträge erkennbar zu machen für das nachfolgende Löschen.</Comment>
    <Argument Name="QueryName">qryF5_HaengeTFmitNeuenAFanGesamtTabelleAn</Argument>
<Comment>Nun werden noch die Rechte derjenigen User behandelt, die bislang in der Importtabelle nicht berücksichtigt worden sind. Dies können (eigentlich) nur noch Rechte bislang unbekannter User sein, denn alle anderen Kombinationen sollten vorher behandelt worden sein. Dazu werden diese Rechte zunächst mit dem Flag "angehaengtSonst" markiert:</Comment>
    <Argument Name="QueryName">qryF5_FlaggeTFmitNeuenAFinImportTabelleUnbekannteUser</Argument>
<Comment>Jetzt sehen wir uns die Plattform an, die in der Importliste auftauchen und hängen gegebenenfalls fehlende Einträge an die Plattform-Tabelle an.</Comment>
    <Argument Name="QueryName">qryF5_AktualisierePlattformListe</Argument>
    <Argument Name="QueryName">qryF5_HaengeTFvonNeuenUsernAnGesamtTabelleAn</Argument>
<Comment>Importiert und angehängt haben wir alles. Was noch fehlt, ist das Markieren derjenigen Einträge, die bislang bekannt waren, aber in der Importtabelle nicht mehr auftauchen. Dabei handelt es sich um gelöschte Rechte oder gelöschte User. Um die Nachvollziehbarkeit erhalten zu können, wird in der nachfolgenden Abfrage nur das "gelöscht"-Flag gesetzt, aber kein Eintrag entfernt. Da wir nicht wissen, ab wann das Element gelöscht wurde, sondern nur den Tagesstand des Importabzugs kennen, wird ein separates Löschdatum gesetzt. Damit bleiben im Datensatz das Einstellungsdatum und das letzte Wiederfinde-Datum erhalten, das muss reichen.Die Abfrage greift nur auf TFs von Usern zurück, die sich auch in der Importtabelle befinden (sonst würden u.U. Rechte von anderen User ebenfalls auf "gelöscht" gesetzt). Das führt dazu, dass TFs von nicht mehr existenten Usern hiervon  nicht markiert werden. Dazu gibt es aber in der Oberfläche den Button "gelöschte User entfernen".</Comment>
    <Argument Name="QueryName">qryF8_SetzeLoeschFlagInGesamtTabelle</Argument>
<Comment>Dann werden noch die Standardwerte für die rvm_ und RVA_00005 Einträge auf "Bleibt (Control-SA)" gesetzt, denn das ist Vorgabe von BM. Was eigentlich auch automatisch gesetzt werden sollte, sind die rvo_ Rechte, aber die sind extrem fehlerhaft modelliert. Deshalb lassen wir erst mal die Finger davon.</Comment>
    <Argument Name="QueryName">qryF5_AktualisiereRVM_</Argument>
    <Argument Name="QueryName">qryF5_AktualisiereRVO_00005</Argument>
    <Argument Name="QueryName">qryF8_SE_RechtesucheVorbereiten0</Argument>
    <Argument Name="QueryName">qryF8_SE_RechtesucheVorbereiten0a</Argument>
    <Argument Name="QueryName">qryF8_SE_RechtesucheVorbereiten0b</Argument>
<Comment>Jetzt müssen zum Abschluss noch in denjenigen importierten Zeilen, bei denen die TFs undbekannt sind, das Modell auf "neues Recht" gesetzt werden. Die sind daran zu erkennen, dass das Modell NULL ist.</Comment>
    <Argument Name="QueryName">qryF6_TFnichtGefundenBeiImport</Argument>
<Comment> Und fertig sind wir.</Comment>


