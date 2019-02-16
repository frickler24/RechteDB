# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# In dieser Datei sollen die Quellen der Stored-Procedures liegen, die zum DBMS deployed werden

from django.shortcuts import render
from django.db import connection
import sys

from django.contrib.auth.decorators import login_required


def push_sp(name, sp, procs_schon_geladen):
	"""
	Speichere eine als Parameter übergebene Stored Procedure

	:param name: Name der zu löschenden Stored_Procedure
	:param sp: Die Stored Procedure, die gespeichert werden soll (SQL-Mengen-String)
	:return: Fehler (False = kein Fehler)
	"""
	# ToDo Das Löschen wirft Warnings im MySQL-Treiber, wenn die SP gar nicht existiert. -> Liste lesen und checken
	fehler = False
	loeschstring = 'DROP PROCEDURE IF EXISTS {}'.format(name)
	with connection.cursor() as cursor:
		try:
			if procs_schon_geladen:
				cursor.execute (loeschstring)
			cursor.execute (sp)
		except:
			e = sys.exc_info()[0]
			fehler = 'Error in push_sp(): {}'.format(e)

		cursor.close()
		return fehler

def push_sp_test(procs_schon_geladen):
	sp = """
CREATE PROCEDURE anzahl_import_elemente()
BEGIN
  SELECT COUNT(*) FROM `tblRechteNeuVonImport`;
END
"""
	return push_sp ('anzahl_import_elemente', sp, procs_schon_geladen)

def call_sp_test():
	fehler = False
	with connection.cursor() as cursor:
		try:
			cursor.execute ("CALL anzahl_import_elemente")
			liste = cursor.fetchone()
		except:
			e = sys.exc_info()[0]
			fehler = 'Error: {}'.format(e)

		cursor.close()
		return fehler or not liste[0] >= 0

def push_sp_vorbereitung(procs_schon_geladen):
	sp = """
create procedure vorbereitung()
BEGIN
    /*
        Die Daten werden zunächst in eine Hilfstabelle tblRechteNeuVonImport eingelesen
        und dann von dort in die vorher geleerte tblRechteAMNeu kopiert.
        tblRechteAMNeu ist ab dann die Arbeitsdatei für alle weiteren Vorgänge,
        die Hilfsdatei wird nicht mehr benutzt.Dieser Zwischenschritt war früher erforderlich,
        weil der gespeicherte Import die Tabelle komplett geloescht hat
        (also eine DROP - CREATE - Sequenz durchlief),
        damit waren die Datentypangaben und Referenzen futsch.
        Heute wird enur noch genutzt, um die doppelt eingelesenen Zeilen zu entfernen
        und dynamische Werte zu erzeugen.
    */

    /*

        Da einige der Importzeilen defekt sind und
        damit der Import und due Ergebnismengen merkwürdig erscheinen,
        hier der Suchstring für den vi:

        /^`\^\d+;]

        Alternativ Suche nach "der Protokolle" und drei Zeilenteile joinen
        Dann suchen nach \Transfer\; und die Einzelnen Back-Slashes gegen doppelte tauschen  
    */

    /*

    TRUNCATE `tblRechteNeuVonImport`;
    LOAD DATA LOCAL INFILE '/tmp/phpbojCHf'     -- ACHTUNG ToDO Die Daten wirklich vom File einlesen
        INSERT INTO TABLE `tblRechteNeuVonImport`
        FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\' LINES TERMINATED BY '\n'
        IGNORE 1 LINES;
    */


    /*
        Seit IIQ werden die wirklichen useriden nicht mehr unter der Identität gehalten,
        sondern unter `AF zugewiesen an Account-name`. Das müssen wir in die userid
        umkopieren, wo nötig.
    */
    UPDATE tblRechteNeuVonImport
        SET `AF zugewiesen an Account-name` = `Identität`
    WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-name` Is Null
        Or tblRechteNeuVonImport.`AF zugewiesen an Account-name` = "";

    /*
        Da hat es wohl mal Irritationen mit useriden gegeben:
        Technische User wurden mit anderen useriden angezeigt, als XV86-er Nummern
        Das wird hier korrigiert.
    */


    UPDATE tblRechteNeuVonImport
        SET tblRechteNeuVonImport.`AF zugewiesen an Account-name` = `Identität`
    WHERE tblRechteNeuVonImport.`Identität` Like 'xv86%'
        AND tblRechteNeuVonImport.`AF zugewiesen an Account-name` Not Like 'xv86%';

    /*
        zum Nachschauen

    select `Identität`, `AF zugewiesen an Account-name` from tblRechteNeuVonImport
    WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-name` Not Like 'xv86%'
        AND `tblRechteNeuVonImport`.`Identität` Like 'xv86%';
    */

    /*
        Leeren und Füllen der eigentlichen Importtabelle
        Einschließlich Herausfiltern der doppelten Zeilen
        (> 1% der Zeilen werden aus IIQ doppelt geliefert)
    */
    create temporary table qryF3_RechteNeuVonImportDuplikatfrei as
        SELECT `AF zugewiesen an Account-name` 		AS userid,
               CONCAT(`Nachname`,', ',`Vorname`) 	AS name,
               `tf name` 							AS tf,
               `tf beschreibung` 					AS tf_beschreibung,
               `AF Anzeigename` 					AS enthalten_in_af,
               `tf kritikalität` 					AS tf_kritikalitaet,
               `tf eigentümer org` 					AS tf_eigentuemer_org,
               `tf Applikation` 					AS tf_technische_plattform,
               `GF name` 							AS GF,
               'gibt es nicht mehr' 				AS vip,
               'gibt es nicht mehr'					AS zufallsgenerator,
               `af gültig ab`						AS af_gueltig_ab,
               `af gültig bis`						AS af_gueltig_bis,
               `direct connect`						AS direct_connect,
               `höchste kritikalität tf in af`		AS hk_tf_in_af,
               `gf beschreibung`					AS gf_beschreibung,
               `af zuweisungsdatum`					AS af_zuweisungsdatum
        FROM tblRechteNeuVonImport
        GROUP BY `userid`,
                 `tf`,
                 `enthalten_in_af`,
                 `tf_technische_plattform`,
                 `GF`;

    /*
        ALTER TABLE `RechteDB`.`qryF3_RechteNeuVonImportDuplikatfrei`
            ADD PRIMARY KEY (`userid`, `tf`(70), `enthalten_in_af`(30), `tf_technische_plattform`, `GF`);
    */


    TRUNCATE table tblRechteAMNeu;
    INSERT INTO tblRechteAMNeu (userid, name, tf, `tf_beschreibung`, `enthalten_in_af`, `tf_kritikalitaet`,
                `tf_eigentuemer_org`, `tf_technische_plattform`, GF, `vip`, zufallsgenerator,
                `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`, `hk_tf_in_af`,
                `gf_beschreibung`, `af_zuweisungsdatum`, doppelerkennung)
    SELECT qryF3_RechteNeuVonImportDuplikatfrei.userid,
           qryF3_RechteNeuVonImportDuplikatfrei.name,
           qryF3_RechteNeuVonImportDuplikatfrei.tf,
           qryF3_RechteNeuVonImportDuplikatfrei.`tf_beschreibung`,
           qryF3_RechteNeuVonImportDuplikatfrei.`enthalten_in_af`,
           qryF3_RechteNeuVonImportDuplikatfrei.`tf_kritikalitaet`,
           qryF3_RechteNeuVonImportDuplikatfrei.`tf_eigentuemer_org`,
           qryF3_RechteNeuVonImportDuplikatfrei.`tf_technische_plattform`,
           qryF3_RechteNeuVonImportDuplikatfrei.GF,
           qryF3_RechteNeuVonImportDuplikatfrei.`vip`,
           qryF3_RechteNeuVonImportDuplikatfrei.zufallsgenerator,
           qryF3_RechteNeuVonImportDuplikatfrei.`af_gueltig_ab`,
           qryF3_RechteNeuVonImportDuplikatfrei.`af_gueltig_bis`,
           qryF3_RechteNeuVonImportDuplikatfrei.`direct_connect`,
           qryF3_RechteNeuVonImportDuplikatfrei.`hk_tf_in_af`,
           qryF3_RechteNeuVonImportDuplikatfrei.`gf_beschreibung`,
           qryF3_RechteNeuVonImportDuplikatfrei.`af_zuweisungsdatum`,
           0
    FROM qryF3_RechteNeuVonImportDuplikatfrei
    ON DUPLICATE KEY UPDATE doppelerkennung=doppelerkennung+1;

    -- Hä#ufig gefundene Fehlermeldung vor Anpassung von Feldlängen und Indizes (bes. GF schien zu kurz gewesen zu sein)
    -- #1062 - Doppelter Eintrag 'AV00087-#B91MADM-rva_01219_beta91_job_abst-RACF - P-rvg_01219_be' für Schlüssel 'für _5b_'

    /*
        Beim Kopieren ist wichtig, dass die Felder,
        die später in JOINs verwendet werden sollen,
        keine NULL-Werte enthalten.
        Das wird durch die nachfolgenden simplen Korrektur-SQLs sichergestellt.
    */

    UPDATE tblRechteAMNeu SET `tf_beschreibung` = 'ka' WHERE `tf_beschreibung` Is Null Or `tf_beschreibung` = '';
    UPDATE tblRechteAMNeu SET `enthalten_in_af` = 'ka' WHERE `enthalten_in_af` Is Null or `enthalten_in_af`  ='';
    UPDATE tblRechteAMNeu SET `tf` = 'Kein name' WHERE `tf` Is Null or `tf`  = '';
    UPDATE tblRechteAMNeu SET `tf_technische_plattform` = 'Kein name' WHERE `tf_technische_plattform` Is Null or `tf_technische_plattform`  = '';
    UPDATE tblRechteAMNeu SET `tf_kritikalitaet` = 'ka' WHERE `tf_kritikalitaet` Is Null or  `tf_kritikalitaet` = '';
    UPDATE tblRechteAMNeu SET `tf_eigentuemer_org` = 'ka' WHERE `tf_eigentuemer_org` Is Null or  `tf_eigentuemer_org` = '';
    UPDATE tblRechteAMNeu SET `GF` = 'k.A.' WHERE GF Is Null or GF = '';
    UPDATE tblRechteAMNeu SET `vip` = 'k.A.' WHERE `vip` Is Null or  `vip` = '';
    UPDATE tblRechteAMNeu SET `zufallsgenerator` = 'k.A.' WHERE `zufallsgenerator` Is Null or `zufallsgenerator` = '';


    /*
    -- Sollte nun 0 ergeben:
    select count(*) from tblRechteAMNeu
        WHERE `tf_beschreibung` Is Null Or `tf_beschreibung` = ''
        or `enthalten_in_af` Is Null or `enthalten_in_af`  = ''
        or `tf` Is Null or `tf`  = ''
        or `tf_technische_plattform` Is Null or `tf_technische_plattform`  = ''
        or `tf_kritikalitaet` Is Null or  `tf_kritikalitaet` = ''
        or `tf_eigentuemer_org` Is Null or  `tf_eigentuemer_org` = ''
        or GF Is Null or GF = ''
        or `vip` Is Null or  `vip` = ''
        or `zufallsgenerator` Is Null or `zufallsgenerator` = '';
    */

    /*
        Erzeuge die Liste der erlaubten Arbeitsplatzfunktionen.
        Sie wird später in der Rollenbehandlung benötigt.
    */
    CALL erzeuge_af_liste;

    /*
        Bis hierhin ging die Vorbereitung.
        Die nächsten Schritte müssen manuell und visuell unterstützt werden:
            - Sichtung der neu hinzugekommenen useriden,
            - Übernahme in die userid-Liste
            - Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf geloescht werden sollen
    */
END
"""
	return push_sp ('vorbereitung', sp, procs_schon_geladen)

def push_sp_neueUser(procs_schon_geladen):
	sp = """
create procedure neueUser (IN orga char(32))
BEGIN

    /*
        Bis hierhin ging die Vorbereitung.
        Die nächsten Schritte müssen manuell und visuell unterstützt werden:
            - Sichtung der neu hinzugekommenen useriden,
            - Übernahme in die userid-Liste
            - Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf geloescht werden sollen
    */
    /*
        Zunächst die Suche nach neu hinzugekommenen Usern:
    */


    /*
        Dieses Statement wird aufgerufen, nachdem die CSV-Daten eingeleesen wurden ('vorbereitung'
        und bevor der "Neue User speichern" Button angeklickt wird.
        Zunächst werden die User in eine temporäre Tabelle geschrieben,
        die in der Importliste auftauchen und
            die nicht in der User-Tabelle auftauchen (die beiden ersten Zeilen im WHERE), oder
            die in der User-Tabelle vorhanden, aber auf "geloescht" gesetzt sind (dritte Zeile im WHERE),
        Der Vergleich erfolgt sowohl über über name als auch userid,
        damit auch erneut vergebene useriden auffallen.

        Gefundene, aber als geloescht markierte User sollen reaktiviert,
        die anderen an die vorhandene User-Tabelle angehängt werden.
        Dies geschieht aber erst im nächsten Schritt 'behandleUser'.
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a as
        SELECT DISTINCT tblRechteAMNeu.userid as userid1,
                        tblRechteAMNeu.name as name1,
                        '35' AS Ausdr1,
                        orga AS Ausdr2,
                        tblUserIDundName.userid as userid2,
                        tblUserIDundName.name as name2,
                        tblUserIDundName.geloescht
        FROM tblRechteAMNeu
            LEFT JOIN tblUserIDundName
            ON tblRechteAMNeu.userid = tblUserIDundName.userid
            AND tblUserIDundName.name = tblRechteAMNeu.name

        WHERE (tblRechteAMNeu.userid    IS NOT NULL AND tblUserIDundName.userid IS NULL)
            OR (tblRechteAMNeu.name     IS NOT NULL AND tblUserIDundName.name   IS NULL)
            OR tblUserIDundName.`geloescht` = TRUE;

    /*
        Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf geloescht werden sollen
        Erst einmal werden die Rechte der als zu löschen markierten User in die Historientabelle verschoben.

        ToDo: Mal checken, ob wir die Tabelle wirklich materialisiert benötigen oder nicht (evtl. zur Ansicht?)
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a as
    SELECT A.userid, A.name, A.`zi_organisation`
        FROM tblUserIDundName A
        WHERE   A.`zi_organisation` = orga
            AND COALESCE(A.geloescht, FALSE) = FALSE
            AND A.userid not in (select distinct userid from tblRechteAMNeu)
        GROUP BY
            A.userid,
            A.name,
            A.`zi_organisation`
    ;

    -- SELECT * from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;

    -- Ein bisschen Statistik für den Anwender
    
    -- select count(*) INTO anzahlNeueUser from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    -- select count(*) INTO anzahlGeloeschteUser from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    -- select count(*) INTO anzahlGeleseneRechte from tblRechteNeuVonImport;
    -- select count(*) INTO anzahlRechteInAMneu from tblRechteAMNeu;

    select 'Anzahl neuer User' as name, count(*) as wert from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a 
    UNION
    select 'Anzahl gelöschter User' as name, count(*) as wert from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
    UNION
    select 'Anzahl gelesener Rechte' as name, count(*) as wert from tblRechteNeuVonImport
    UNION
    select 'Anzahl Rechte in AM_neu' as name, count(*) as wert from tblRechteAMNeu
    UNION
    select 'orga' as name, cast(orga as char) as wert
    
    ;
END
"""
	return push_sp ('neueUser', sp, procs_schon_geladen)

def push_sp_behandleUser(procs_schon_geladen):
	sp = """
create procedure behandleUser ()
BEGIN

    create temporary table tbl_tmpGeloeschte as
        SELECT userid1
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
            WHERE `geloescht` = True;

    -- select * from tbl_tmpGeloeschte;

    /*
        Markiere die useriden wieder als aktiv, die bereits bekannt, aber als geloescht markiert sind.
    */
    UPDATE tblUserIDundName
        INNER JOIN tbl_tmpGeloeschte
            ON tbl_tmpGeloeschte.userid1 = tblUserIDundName.userid
    SET tblUserIDundName.geloescht = False;

    /*
        Nun werden die wirklich neuen User an die userid-Tabelle angehängt
        (ehemals qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2 u.a.)
    * /
    create temporary table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2 as
        SELECT userid1, name1, Ausdr1, Ausdr2, geloescht
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
            WHERE (`geloescht` = FALSE or `geloescht` IS NULL)
                AND (userid1 IS NOT NULL OR name1 IS NOT NULL);

    INSERT INTO tblUserIDundName (userid, name, orga_id, `zi_organisation`, geloescht )
        SELECT  userid1,
                name1,
                Ausdr1 AS orga_id,
                Ausdr2 AS `zi_organisation`
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2;
    */
    INSERT INTO tblUserIDundName (userid, name, orga_id, `zi_organisation`, geloescht, gruppe, abteilung )
        SELECT userid1, name1, Ausdr1 AS orga_id, Ausdr2 AS `zi_organisation`, 
        		False AS geloescht, "" as gruppe, "" as abteilung
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
            WHERE COALESCE(`geloescht`, FALSE) = FALSE
                AND (userid1 IS NOT NULL OR name1 IS NOT NULL);


    -- select * from tblUserIDundName;


    /*
        Bevor die alten User als geloescht markiert werden,
        müssen deren derzeit vorhandenen Rechte in die Historientabelle verschoben werden.
    */

    INSERT INTO tblGesamtHistorie (
                `userid_und_name_id`, tf, `tf_beschreibung`, `enthalten_in_af`,
                modell, `tf_kritikalitaet`, `tf_eigentuemer_org`, `af_zuweisungsdatum`,
                plattform_id, GF, geloescht, gefunden, wiedergefunden, geaendert, loeschdatum, neueaf, datum, `id_alt`
            )
    SELECT `tblGesamt`.`userid_und_name_id`,
           `tblGesamt`.tf,
           `tblGesamt`.`tf_beschreibung`,
           `tblGesamt`.`enthalten_in_af`,
           `tblGesamt`.modell,
           `tblGesamt`.`tf_kritikalitaet`,
           `tblGesamt`.`tf_eigentuemer_org`,
           `tblGesamt`.`af_zuweisungsdatum`,
           `tblGesamt`.plattform_id,
           `tblGesamt`.GF,
           `tblGesamt`.`geloescht`,
           `tblGesamt`.gefunden,
           `tblGesamt`.wiedergefunden,
           `tblGesamt`.`geaendert`,
           Now() AS Ausdr1,
           `tblGesamt`.neueaf,
           `tblGesamt`.datum,
           `tblGesamt`.id
        FROM `tblGesamt`
        INNER JOIN (tblUserIDundName
                    inner join qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
                    on qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.userid = tblUserIDundName.userid)
            ON tblUserIDundName.id = `tblGesamt`.`userid_und_name_id`
        WHERE tblUserIDundName.userid IN (SELECT userid FROM `qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a`)
            AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE;


    -- Setzen der Löschflags in der Gesamttabelle für jedes Recht jeder nicht mehr vorhandenen userid

    UPDATE
        tblGesamt
        INNER JOIN (tblUserIDundName
                    inner join qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
                    on qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.userid = tblUserIDundName.userid)
	        ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id
        SET tblGesamt.geloescht = TRUE,
            tblGesamt.`loeschdatum` = Now()
        WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE;

    -- Die zu löschenden User werden in der User-Tabelle nun auf "geloescht" gesetzt

    UPDATE tblUserIDundName
        INNER JOIN qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
            ON qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.userid = tblUserIDundName.userid
        SET `geloescht` = TRUE
        WHERE COALESCE(`geloescht`, FALSE) = FALSE;

    -- ToDo Es fehlt komplett das Löschen der historisierten Rechte für gerade geloeschte User

END
"""
	return push_sp ('behandleUser', sp, procs_schon_geladen)

def push_sp_behandleRechte(procs_schon_geladen):
	sp = """
create procedure behandleRechte (IN orga char(32))
BEGIN

    /*
        Nun folgt der komplexere Block:
        Die neuen, evtl. unveränderten und auch nicht mehr vorhandenen einzelnen Berechtigungen
        müssen schrittweise in die Gesamttabelle eingetragen werden.
    */

    -- Lösche zunächst Plattform-Namen, die in der Gesamttabelle nicht mehr auftauchen
    -- (manchmal werden Plattformen einfach umbenannt)
    CREATE TEMPORARY TABLE bloed as
        SELECT tblPlattform.`tf_technische_plattform` as x
            FROM tblPlattform
            LEFT JOIN tblGesamt ON tblPlattform.id = tblGesamt.plattform_id
            WHERE tblGesamt.plattform_id IS NULL;

    DELETE FROM tblPlattform
    WHERE `tf_technische_plattform` IN (select x from bloed);

    -- Ergänze alle Plattformen, die bislang nur in tblRechteAMNeu bekannt sind
    INSERT INTO tblPlattform (`tf_technische_plattform`)
    SELECT DISTINCT tblRechteAMNeu.`tf_technische_plattform`
    FROM tblRechteAMNeu
        LEFT JOIN tblPlattform
        ON tblRechteAMNeu.`tf_technische_plattform` = tblPlattform.`tf_technische_plattform`
    WHERE tblPlattform.`tf_technische_plattform` IS NULL;

    /*
        Der Status "gefunden" dient dazu,
        später die Selektion neuer Rechte zu vereinfachen und übriggebliebene Rechte zu löschen.
        Er wird sowohl in der Gesamt-Tabelle, als auch in der Importtabelle zurückgesetzt.
        Gleichzeitig wird der Status "geaendert" in beiden Tabellen zurückgesetzt.
    */

    UPDATE tblGesamt
        INNER JOIN tblUserIDundName
        ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id
    SET tblGesamt.gefunden = FALSE,
        tblGesamt.geaendert = FALSE
    WHERE tblGesamt.gefunden = TRUE OR tblGesamt.`geaendert` = TRUE;

    -- Dies hier nur zur Sicherheit - eigentlich müssten die eh null sein
    UPDATE tblRechteAMNeu
    SET tblRechteAMNeu.gefunden = FALSE,
        tblRechteAMNeu.geaendert = FALSE
    WHERE tblRechteAMNeu.gefunden = TRUE
        OR tblRechteAMNeu.geaendert = TRUE;

    /*
        Nun wird die "flache" Tabelle "tbl_Gesamt_komplett" erzeugt.
        Dort sind die Referenzen zu den derzeit existierenden, aktiven 
        User-, Berechtigungs- und Orga-Tabellen aufgelöst,
        allerdings in dieser Implementierung ausschließlich für die benötigten UserIDen
        (früher wirklich komplett).

        ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller userids benötigt wird, sonst löschen nach Nutzung
    */

    drop table if exists tbl_Gesamt_komplett;
	create temporary table uids as
		select distinct userid as uid from tblRechteAMNeu;

    create table tbl_Gesamt_komplett as
		SELECT tblGesamt.id,
               tblUserIDundName.userid,
               tblUserIDundName.name,
               tblGesamt.tf,
               tblGesamt.`tf_beschreibung`,
               tblGesamt.`enthalten_in_af`,
               tblUEbersichtAF_GFs.`name_gf_neu`,
               tblUEbersichtAF_GFs.`name_af_neu`,
               tblGesamt.`tf_kritikalitaet`,
               tblGesamt.`tf_eigentuemer_org`,
               tblPlattform.`tf_technische_plattform`,
               tblGesamt.GF,
               tblGesamt.`vip`,
               tblGesamt.zufallsgenerator,
               tblGesamt.modell,
               tblUserIDundName.orga_id,
               tblUserIDundName.`zi_organisation`,
               tblGesamt.`af_gueltig_ab`,
               tblGesamt.`af_gueltig_bis`,
               tblGesamt.`direct_connect`,
               tblGesamt.`hk_tf_in_af`,
               tblGesamt.`gf_beschreibung`,
               tblGesamt.`af_zuweisungsdatum`,
               tblGesamt.datum,
               tblGesamt.`geloescht`
        FROM tblGesamt
            INNER JOIN tblUEbersichtAF_GFs
            ON tblGesamt.modell = tblUEbersichtAF_GFs.id

            INNER JOIN tblPlattform
            ON tblPlattform.id = tblGesamt.plattform_id

            INNER JOIN tblUserIDundName
            ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id

        WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
            AND tblUserIDundName.userid in (select uid from uids)
        ORDER BY tblGesamt.tf,
                 tblUserIDundName.userid;

    /*
        Markieren der Flags Gefunden in tblRechteAMNeu sowie tblGesamt.
        In letzterer wird auch das wiedergefunden-Datum eingetragen, wann das Recht wiedergefunden wurde.

        Zusätzlich werden alle Felder, die hier nicht zum Vergleich der Rechte-Gleichheit
        genutzt wurden, in der Gesamttabelle aktualisiert.

        Das hat früher mal zu Problemen geführt (Umbenennung ovn Rechten und -Eigentümern), 
        in letzter Zeit aber eher nicht mehr.

    */

    -- Zunächst das Setzen und Kopieren der Daten im Fall "Wiedergefunden"
    UPDATE tblRechteAMNeu
        INNER JOIN tblGesamt
        ON      tblRechteAMNeu.tf = tblGesamt.tf
            AND tblRechteAMNeu.GF = tblGesamt.GF
            AND tblRechteAMNeu.`enthalten_in_af` = tblGesamt.`enthalten_in_af`
            AND tblRechteAMNeu.zufallsgenerator = tblGesamt.zufallsgenerator
            AND tblRechteAMNeu.`vip` = tblGesamt.`vip`

        INNER JOIN tblUserIDundName
        ON      tblUserIDundName.userid = tblRechteAMNeu.userid
            AND tblUserIDundName.id = tblGesamt.`userid_und_name_id`

        INNER JOIN tblPlattform
        ON      tblPlattform.`tf_technische_plattform` = tblRechteAMNeu.`tf_technische_plattform`
            AND tblPlattform.id = tblGesamt.plattform_id

    SET tblGesamt.gefunden = TRUE,
        tblGesamt.Wiedergefunden = Now(),
        tblRechteAMNeu.Gefunden = TRUE,
        tblGesamt.`tf_beschreibung` = `tblRechteAMNeu`.`tf_beschreibung`,
        tblGesamt.`tf_kritikalitaet` = `tblRechteAMNeu`.`tf_kritikalitaet`,
        tblGesamt.`tf_eigentuemer_org` = `tblRechteAMNeu`.`tf_eigentuemer_org`,
        tblGesamt.`af_gueltig_ab` = `tblRechteAMNeu`.`af_gueltig_ab`,
        tblGesamt.`af_gueltig_bis` = `tblRechteAMNeu`.`af_gueltig_bis`,
        tblGesamt.`direct_connect` = `tblRechteAMNeu`.`direct_connect`,
        tblGesamt.`hk_tf_in_af` = `tblRechteAMNeu`.`hk_tf_in_af`,
        tblGesamt.`gf_beschreibung` = `tblRechteAMNeu`.`gf_beschreibung`,
        tblGesamt.`af_zuweisungsdatum` = `tblRechteAMNeu`.`af_zuweisungsdatum`

    WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
        AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE;


    /*
        qryF2setzeGeaentderteAlteAF implementiert den Fall der geaenderten AF aber ansonsten gleichen Daten
    */

    UPDATE tblRechteAMNeu
        INNER JOIN tblGesamt
        ON      tblRechteAMNeu.tf = tblGesamt.tf
            AND tblRechteAMNeu.GF = tblGesamt.GF
            AND tblRechteAMNeu.zufallsgenerator = tblGesamt.zufallsgenerator
            AND tblRechteAMNeu.`vip` = tblGesamt.`vip`

        INNER JOIN tblUserIDundName
        ON      tblUserIDundName.userid = tblRechteAMNeu.userid
            AND tblUserIDundName.id = tblGesamt.`userid_und_name_id`

        INNER JOIN tblPlattform
        ON      tblPlattform.`tf_technische_plattform` = tblRechteAMNeu.`tf_technische_plattform`
            AND tblPlattform.id = tblGesamt.plattform_id

    SET tblGesamt.geaendert = TRUE,
        tblRechteAMNeu.geaendert = TRUE,
        tblGesamt.neueaf = `tblRechteAMNeu`.`enthalten_in_af`

    WHERE   tblGesamt.`enthalten_in_af` <> tblRechteAMNeu.`enthalten_in_af`
        AND tblGesamt.gefunden = FALSE
        AND tblRechteAMNeu.Gefunden = FALSE
        AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
        AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
        ;

    /*
        qryF5c_HistorisiereGeaenderteEintraege
        In die Historientabelle werden die zur Änderung vorgemerkten Einträge aus der Gesamttabelle kopiert.
    */

    INSERT INTO tblGesamtHistorie (`userid_und_name_id`, tf, `tf_beschreibung`, `enthalten_in_af`, modell, `tf_kritikalitaet`,
                `tf_eigentuemer_org`, plattform_id, GF, `vip`, zufallsgenerator, geloescht, gefunden,
                wiedergefunden, geaendert, neueaf, datum, `id_alt`, loeschdatum)
    SELECT tblGesamt.`userid_und_name_id`,
           tblGesamt.tf,
           tblGesamt.`tf_beschreibung`,
           tblGesamt.`enthalten_in_af`,
           tblGesamt.modell,
           tblGesamt.`tf_kritikalitaet`,
           tblGesamt.`tf_eigentuemer_org`,
           tblGesamt.plattform_id,
           tblGesamt.GF,
           tblGesamt.`vip`,
           tblGesamt.zufallsgenerator,
           tblGesamt.geloescht,
           tblGesamt.gefunden,
           Now() AS Ausdr1,
           tblGesamt.geaendert,
           tblGesamt.neueaf,
           tblGesamt.datum,
           tblGesamt.id,
           tblGesamt.loeschdatum
    FROM tblUserIDundName
        INNER JOIN tblGesamt
        ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`

    WHERE tblGesamt.`geaendert` = TRUE
           AND tblUserIDundName.`zi_organisation` LIKE orga;      -- ToDo: Wird die Einschränkung wirklich benötigt?
           -- ToDo: Es sollte ja nicht kopiert, sondern verschoben werden. Es fehlt hier also das Löschen.


    /*
        Anschließend können die geaenderten Werte in die GesamtTabelle übernommen werden.
        Dazu wird der Inhalt des kommentarfelds in die AF-alt-Spalte eingetragen.
        Damit müsste das erledigt sein :-)

        qryF5d_AktualisiereGeaenderteAF
    */

    -- ToDo: Später noch mal das geaendert-Flag zurücksetzen, dann entfällt das ToDo vorher...

    UPDATE tblUserIDundName
        INNER JOIN tblGesamt
        ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`
    SET tblGesamt.`enthalten_in_af` = `neueaf`

    WHERE tblGesamt.`geaendert` = TRUE
        AND tblUserIDundName.`zi_organisation` = orga;


    /*
        Als nächstes kann es sein, dass in der Importliste noch tf mit NEUEN AF stehen,
        die zwar bereits in der Gesamtliste bezogen auf die Uid bekannt sind,
        dort aber bereits mit den ALTEN AF-Bezeichnungen gefunden wurden.
        Damit nun nicht bei jedem wiederholten Import die AF-Bezeichnungen umgeschossen werden,
        hängen wir diese Zeilen nun hinten an die Gesamttabelle an.

        Dazu werden im ersten Schritt in der Importtabelle die Zeilen markiert (angehaengt_bekannt),
        die anzuhängen sind. Das sieht zwar umständlich aus, erleichtert aber später die Bewertung.
        ob noch irgendwelche Einträge in der Importtabelle nicht bearbeitet wurden.
        Die Flags kann man eigentlich auch zusammenfassen,
        dann müssten aber bearbeitete Zeilen separat umgeschossen werden...

        Beim Einfügen der neuen tf-AF-Kombinationen wird in der Gesamttabelle "gefunden" gesetzt,
        damit das Recht später nicht gleich wieder geloescht wird.

        ToDo: Eigentlich müssten hierbei auch die GF berücksichtigt werden - da gab es aber noch keine Auffälligkeiten

        qryF5_FlaggetfmitNeuenAFinImportTabelle
    */

    UPDATE tblRechteAMNeu
        INNER JOIN tbl_Gesamt_komplett
        ON (tbl_Gesamt_komplett.zufallsgenerator = tblRechteAMNeu.zufallsgenerator)
            AND (tbl_Gesamt_komplett.`vip` = tblRechteAMNeu.`vip`)
            AND (tblRechteAMNeu.GF = tbl_Gesamt_komplett.GF)
            AND (tblRechteAMNeu.`enthalten_in_af` = tbl_Gesamt_komplett.`enthalten_in_af`)
            AND (tblRechteAMNeu.userid = tbl_Gesamt_komplett.userid)
            AND (tblRechteAMNeu.tf = tbl_Gesamt_komplett.tf)
            AND (tblRechteAMNeu.`tf_technische_plattform` = tbl_Gesamt_komplett.`tf_technische_plattform`)
        SET tblRechteAMNeu.`angehaengt_bekannt` = TRUE
        WHERE tblRechteAMNeu.Gefunden = TRUE
            AND tblRechteAMNeu.`geaendert` = FALSE;

    /*
        Zum Gucken:

    SELECT COUNT(*) FROM tblRechteAMNeu
        INNER JOIN tbl_Gesamt_komplett
        ON (tbl_Gesamt_komplett.zufallsgenerator = tblRechteAMNeu.zufallsgenerator)
            AND (tbl_Gesamt_komplett.`vip` = tblRechteAMNeu.`vip`)
            AND (tblRechteAMNeu.GF = tbl_Gesamt_komplett.GF)
            AND (tblRechteAMNeu.`enthalten_in_af` = tbl_Gesamt_komplett.`enthalten_in_af`)
            AND (tblRechteAMNeu.userid = tbl_Gesamt_komplett.userid)
            AND (tblRechteAMNeu.tf = tbl_Gesamt_komplett.tf)
            AND (tblRechteAMNeu.`tf_technische_plattform` = tbl_Gesamt_komplett.`tf_technische_plattform`)
        WHERE tblRechteAMNeu.Gefunden = TRUE
            AND tblRechteAMNeu.`geaendert` = FALSE;
    */

    /*
        Anschließend werden diese selektierten Zeilen an die Gesamttabelle angehängt.
        Dabei wird in der Gesamttabelle das Flag "gefunden" gesetzt,
        um diese Einträge erkennbar zu machen für das nachfolgende Löschen alter Einträge.

        qryF5_HaengetfmitNeuenAFanGesamtTabelleAn
    */

    INSERT INTO tblGesamt (tf, `tf_beschreibung`, `enthalten_in_af`, datum, modell, `userid_und_name_id`,
                plattform_id, Gefunden, `geaendert`, `tf_kritikalitaet`, `tf_eigentuemer_org`, GF, `vip`,
                zufallsgenerator, `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`, `hk_tf_in_af`,
                `gf_beschreibung`, `af_zuweisungsdatum`, letzte_aenderung)
    SELECT  tblRechteAMNeu.tf,
            tblRechteAMNeu.`tf_beschreibung`,
            tblRechteAMNeu.`enthalten_in_af`,
            Now() AS datumNeu,
            (
                SELECT DISTINCT modell
                FROM `tblGesamt`
                WHERE `tblGesamt`.`userid_und_name_id` = (
                    SELECT DISTINCT id
                    FROM tblUserIDundName
                    WHERE userid = tblRechteAMNeu.userid
                )
                AND `tblGesamt`.`tf` = `tblRechteAMNeu`.`tf`
                LIMIT 1
            ) AS modellNeu,

            (SELECT id FROM tblUserIDundName WHERE userid = tblRechteAMNeu.userid) AS UidnameNeu,

            (SELECT id FROM tblPlattform
                WHERE `tf_technische_plattform` = tblRechteAMNeu.`tf_technische_plattform`) AS PlattformNeu,
            TRUE AS Ausdr1,
            tblRechteAMNeu.`geaendert`,
            tblRechteAMNeu.`tf_kritikalitaet`,
            tblRechteAMNeu.`tf_eigentuemer_org`,
            tblRechteAMNeu.GF,
            tblRechteAMNeu.`vip`,
            tblRechteAMNeu.zufallsgenerator,
            tblRechteAMNeu.`af_gueltig_ab`,
            tblRechteAMNeu.`af_gueltig_bis`,
            tblRechteAMNeu.`direct_connect`,
            tblRechteAMNeu.`hk_tf_in_af`,
            tblRechteAMNeu.`gf_beschreibung`,
            tblRechteAMNeu.`af_zuweisungsdatum`,
            now() as letzte_aenderung

    FROM tblRechteAMNeu
    WHERE tblRechteAMNeu.Gefunden = FALSE
        AND tblRechteAMNeu.`angehaengt_bekannt` = TRUE;

    /*
        Nun werden noch die Rechte derjenigen User behandelt,
        die bislang in der Importtabelle nicht berücksichtigt worden sind.
        Dies können nur noch Rechte bislang unbekannter User
        oder unbekannte Rechte bekannter User sein.
        Dazu werden diese Rechte zunächst mit dem Flag "angehaengt_sonst" markiert:

        qryF5_FlaggetfmitNeuenAFinImportTabelleUnbekannteUser
    */


    /*
    select * from tblRechteAMNeu
    WHERE COALESCE(Gefunden, FALSE) = FALSE
        AND COALESCE(geaendert, FALSE) = FALSE
        AND COALESCE(angehaengt_bekannt, FALSE) = FALSE;
    */

    UPDATE tblRechteAMNeu
    SET `angehaengt_sonst` = TRUE
    WHERE COALESCE(Gefunden, FALSE) = FALSE
        AND COALESCE(geaendert, FALSE) = FALSE
        AND COALESCE(angehaengt_bekannt, FALSE) = FALSE;

    /*
    select * from tblRechteAMNeu
    WHERE angehaengt_sonst = TRUE;
    */

    /*
        Jetzt sehen wir uns die Plattform an, die in der Importliste auftauchen
        und hängen gegebenenfalls fehlende Einträge an die Plattform-Tabelle an.

        qryF5_AktualisierePlattformListe
    */

    INSERT INTO tblPlattform (`tf_technische_plattform`)
    SELECT DISTINCT tblRechteAMNeu.`tf_technische_plattform`
    FROM tblRechteAMNeu
        LEFT JOIN tblPlattform
        ON tblRechteAMNeu.`tf_technische_plattform` = tblPlattform.`tf_technische_plattform`
        WHERE tblPlattform.`tf_technische_plattform` IS NULL;


    /*
        Nun werden alle neuen Rechte aller User an die Gesamttabelle angehängt.
        Der alte query-name weist irrtümlich darauf hin, dass nur neue User hier behandelt würden,
        das ist aber definitiv nicht so.

        qryF5_HaengetfvonNeuenUsernAnGesamtTabelleAn
    */

    INSERT INTO tblGesamt (tf, `tf_beschreibung`, `enthalten_in_af`, datum, modell, `userid_und_name_id`,
                plattform_id, Gefunden, `geaendert`, `tf_kritikalitaet`, `tf_eigentuemer_org`, geloescht, GF,
                `vip`, zufallsgenerator, `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`,
                `hk_tf_in_af`, `gf_beschreibung`, `af_zuweisungsdatum`, letzte_aenderung)
    SELECT  tblRechteAMNeu.tf,
            tblRechteAMNeu.`tf_beschreibung`,
            tblRechteAMNeu.`enthalten_in_af`,
            Now() AS datumNeu,

            (SELECT `id` FROM `tblUEbersichtAF_GFs` WHERE `name_af_neu` LIKE 'Neues Recht noch nicht eingruppiert') AS modellNeu,

            (SELECT id FROM tblUserIDundName WHERE userid = tblRechteAMNeu.userid) AS UidnameNeu,

            (SELECT id FROM tblPlattform
                WHERE `tf_technische_plattform` = tblRechteAMNeu.`tf_technische_plattform`) AS PlattformNeu,

            TRUE AS Ausdr1,
            FALSE AS Ausdr2,
            tblRechteAMNeu.`tf_kritikalitaet`,
            tblRechteAMNeu.`tf_eigentuemer_org`,
            FALSE AS Ausdr3,
            tblRechteAMNeu.GF,
            tblRechteAMNeu.`vip`,
            tblRechteAMNeu.zufallsgenerator,
            tblRechteAMNeu.`af_gueltig_ab`,
            tblRechteAMNeu.`af_gueltig_bis`,
            tblRechteAMNeu.`direct_connect`,
            tblRechteAMNeu.`hk_tf_in_af`,
            tblRechteAMNeu.`gf_beschreibung`,
            tblRechteAMNeu.`af_zuweisungsdatum`,
            now() as letzte_aenderung
    FROM tblRechteAMNeu
    WHERE tblRechteAMNeu.`angehaengt_sonst` = TRUE;


    /*
        Importiert und angehängt haben wir alles.
        Was noch fehlt, ist das Markieren derjenigen Einträge,
        die bislang bekannt waren, aber in der Importtabelle nicht mehr auftauchen.

        Dabei handelt es sich um geloeschte Rechte oder geloeschte User.

        Um die Nachvollziehbarkeit erhalten zu können,
        wird in der nachfolgenden Abfrage nur das "geloescht"-Flag gesetzt, aber kein Eintrag entfernt.
        Da wir nicht wissen, ab wann das Element geloescht wurde,
        sondern wir nur den Tagesstand des Importabzugs kennen, wird ein separates loeschdatum gesetzt.
        Damit bleiben im Datensatz das Einstellungsdatum und das letzte Wiederfinde-datum erhalten, das muss reichen.

        Die Abfrage greift nur auf tfs von Usern zurück, die sich auch in der Importtabelle befinden
        (sonst würden u.U. Rechte von anderen User ebenfalls auf "geloescht" gesetzt).
        Das führt dazu, dass tfs von nicht mehr existenten Usern hiervon nicht markiert werden.
        Dazu gibt es aber die Funktion "geloeschte User entfernen", die vorher genutzt wurde.

        qryF8_SetzeLoeschFlagInGesamtTabelle
    */

    UPDATE tblUserIDundName
        INNER JOIN tblGesamt
        ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`
            AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
            AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
            AND COALESCE(tblGesamt.gefunden, FALSE) = FALSE
            AND COALESCE(tblGesamt.`geaendert`, FALSE) = FALSE
            AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE

    SET tblGesamt.geloescht = TRUE,
        tblGesamt.loeschdatum = Now()

    WHERE tblUserIDundName.userid IN (SELECT `userid` FROM `tblRechteAMNeu` WHERE `userid` = `tblUserIDundName`.`userid`);


    /*
        Dann werden noch die Standardwerte für die rvm_ und RVA_00005 Einträge auf "Bleibt (Control-SA)" gesetzt,
        denn das ist Vorgabe von BM.

        Was eigentlich auch automatisch gesetzt werden sollte, sind die rvo_ Rechte,
        aber die sind extrem fehlerhaft modelliert.
        Deshalb lassen wir bis auf das AI-Recht erst mal die Finger davon.

        qryF5_AktualisiereRVM_

        qryF5_AktualisiereRVO_00005 wurde nicht mit übernommen,
        weil die rvo_Rechte nun in der neuen modellierung berücksichtigt werden
    */

    UPDATE tblGesamt,
           tblUEbersichtAF_GFs
    SET tblGesamt.modell = `tblUEbersichtAF_GFs`.`id`
    WHERE tblGesamt.`enthalten_in_af` LIKE "rvm_*"
        AND tblUEbersichtAF_GFs.`name_gf_neu` = "Bleibt (Control-SA)"
        AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE;

    /*
        Jetzt müssen zum Abschluss noch in denjenigen importierten Zeilen,
        bei denen die tfs unbekannt sind, das modell auf "neues Recht" gesetzt werden.
        Die sind daran zu erkennen, dass das modell NULL ist.
    */

    UPDATE tblGesamt,
           tblUEbersichtAF_GFs
    SET tblGesamt.modell = `tblUEbersichtAF_GFs`.`id`
    WHERE tblUEbersichtAF_GFs.`name_gf_neu` = "Neues Recht noch nicht eingruppiert"
       AND tblGesamt.modell IS NULL;


/*
    Und fertig wir sind.
*/
END
"""
	return push_sp ('behandleRechte', sp, procs_schon_geladen)

def push_sp_loescheDoppelteRechte(procs_schon_geladen):
	sp = """
create procedure loescheDoppelteRechte (IN nurLesen bool)
BEGIN
    /*
        Prozedur zum Finden und Löschen doppelt vorhandener Einträge in der Gesamttabelle.
        Auch wenn das eigentlich ie vorkommen dürfte, passiert das dennoch ab und an.
        Hauptgruind sind falsch formatierte Eingatelisten.
    */

    CREATE temporary table qryF3_DoppelteElementeFilterAusGesamtTabelle as
        SELECT DISTINCT b.id,
            b.tf,
            a.geloescht as RechtGeloescht,
            b.geloescht as UserGeloescht,
            tblUserIDundName.userid,
            tblUserIDundName.name,
            a.GF,
            a.vip,
            a.zufallsgenerator

            FROM tblGesamt AS b,
                tblUserIDundName
                INNER JOIN tblGesamt AS a
                    ON tblUserIDundName.id = a.userid_und_name_id
            WHERE a.id < b.id
                AND COALESCE(a.geloescht, FALSE) = FALSE
                AND COALESCE(a.geloescht, FALSE) = FALSE
                AND a.GF = b.gf
                AND a.vip = b.vip
                AND a.zufallsgenerator = b.zufallsgenerator
                AND a.userid_und_name_id =b.userid_und_name_id
                AND a.tf = b.tf
                AND a.enthalten_in_af = b.enthalten_in_af
                AND a.tf_beschreibung = b.tf_beschreibung
                AND a.plattform_id = b.plattform_id
                AND a.tf_kritikalitaet = b.tf_kritikalitaet
                AND a.tf_eigentuemer_org = b.tf_eigentuemer_org;

    IF (COALESCE(nurlesen, false) = True)
    THEN
        select count(*) from qryF3_DoppelteElementeFilterAusGesamtTabelle;
    ELSE
        UPDATE tblGesamt
        	INNER JOIN qryF3_DoppelteElementeFilterAusGesamtTabelle
            ON tblGesamt.id = qryF3_DoppelteElementeFilterAusGesamtTabelle.id
            
            SET tblGesamt.geloescht = True,
	            tblGesamt.patchdatum = Now()
			WHERE COALESCE(tblGesamt.geloescht, FALSE) = False;
    END IF;
END
"""
	return push_sp ('loescheDoppelteRechte', sp, procs_schon_geladen)

def push_sp_nichtai(procs_schon_geladen):
	sp = """
create procedure setzeNichtAIFlag()
BEGIN

    /*
        Das Flag, ob ein Recht sich auf einen AI-User bezieht, wird korrigiert

        qryF8_SE_RechtesucheVorbereiten0

        ToDo: Keine Ahnung mehr, wozu das Nicht-AI-Flag gedient hat. Prüfung und ggfs. enfernen. Die Suchabfrage scheint auch kompletter Unfug zu sein.
    */

    UPDATE tblGesamt
        INNER JOIN tblUserIDundName
        ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id
        AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
        AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE

    SET tblGesamt.`nicht_ai` = FALSE

    WHERE tblGesamt.`nicht_ai` = TRUE
        AND tblUserIDundName.userid IN (SELECT DISTINCT tblRechteAMNeu.userid FROM tblRechteAMNeu);

    /*
        Die nächsten vier temporären Tabellen dienen einem einzigen Zweck:

        Für alle derzeit betrachteten Rechte wird in der Gesamttabelle festgehalten,
        welche für AI sind und welche nicht.

        Das wurde wohl früher mal für SE-modellierungen genutzt.

        Dazu werden die folgenden temporären Queries erzeugt:

        qryF7_GesamtNachtfunduserid:   Enthält "eigentlich" alle Daten zur ordentlichen Anzeige.
            Dem Namen nach müssten die Daten genau so sortiert sein wie angegeben,
            aber in unserem Fall hier kostet das nur Laufzeit und wird nicht benötigt.

        ToDo: Ein paar Daten-Fehler hierbei...

        / *
        -------------
        Suchstring nach 6 verlorenen Rechten


        select tblGesamt.id as gesamtid, qryF7_GesamtNachtfunduserid.id as tmpid
        from tblGesamt
        left join qryF7_GesamtNachtfunduserid
            on tblGesamt.id = qryF7_GesamtNachtfunduserid.id
        where tblGesamt.geloescht = False
        AND qryF7_GesamtNachtfunduserid.id is null

        * /


        ToDO Löschen der Query nach Prüfung
    */


    -- qryF7_GesamtNachtfunduserid liefert eine Rechteliste der aktiven User aus der Gesamttabelle
    drop table if exists qryF7_GesamtNachtfunduserid;
    create table qryF7_GesamtNachtfunduserid AS
        SELECT tblOrga.`team`,
               tblGesamt.id,
               tblGesamt.tf,
               tblGesamt.`userid_und_name_id`,
               tblGesamt.`tf_beschreibung`,
               tblGesamt.`enthalten_in_af`,
               tblGesamt.modell,
               tblGesamt.`tf_kritikalitaet`,
               tblGesamt.`tf_eigentuemer_org`,
               tblGesamt.plattform_id,
               tblUserIDundName.`zi_organisation`,
               tblGesamt.datum,
               tblGesamt.gefunden,
               tblGesamt.wiedergefunden,
               tblGesamt.geaendert,
               tblGesamt.neueaf,
               tblGesamt.`nicht_ai`

        FROM tblGesamt
            INNER JOIN tblUEbersichtAF_GFs
                ON tblGesamt.modell = tblUEbersichtAF_GFs.id

            INNER JOIN tblPlattform
                ON tblGesamt.plattform_id = tblPlattform.id

            INNER JOIN (tblUserIDundName INNER JOIN tblOrga ON tblUserIDundName.orga_id = tblOrga.id)
                ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id

        WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
            AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE

        -- ORDER BY tblGesamt.tf, tblGesamt.`userid_und_name_id`
    ;
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachtfunduserid` ADD PRIMARY KEY (`id`);
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachtfunduserid` ADD KEY tf (`tf`);
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachtfunduserid` ADD KEY userid (`userid_und_name_id`);


    -- qryF8_SE_RechtesucheVorbereiten1 liefert alle tfen distinct, die bei Usern von AI verwendet werden
    drop table if exists qryF8_SE_RechtesucheVorbereiten1;
    create table qryF8_SE_RechtesucheVorbereiten1 AS
        SELECT distinct tblGesamt.tf
        FROM tblUserIDundName
        INNER JOIN tblGesamt
            ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`

        WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
            AND tblUserIDundName.`zi_organisation` LIKE "ai%";
    ALTER TABLE `RechteDB`.`qryF8_SE_RechtesucheVorbereiten1` ADD PRIMARY KEY (`tf`);

    -- Nun wird eine Liste mit Rechten zusammengestellt,
    -- die nicht von AI sind.
    -- ToDo: Gruseliges SQL entwirren

    drop table if exists qryF8_SE_RechteOhneVerwendungInAI;
    create table qryF8_SE_RechteOhneVerwendungInAI AS
        SELECT DISTINCT tblUserIDundName.name,
                        tblUserIDundName.userid,
                        qryF7_GesamtNachtfunduserid.tf,
                        qryF7_GesamtNachtfunduserid.`tf_beschreibung`,
                        qryF7_GesamtNachtfunduserid.`enthalten_in_af`,
                        qryF7_GesamtNachtfunduserid.modell,
                        qryF7_GesamtNachtfunduserid.`tf_kritikalitaet`,
                        qryF7_GesamtNachtfunduserid.`tf_eigentuemer_org`,
                        qryF7_GesamtNachtfunduserid.plattform_id,
                        qryF7_GesamtNachtfunduserid.datum,
                        qryF7_GesamtNachtfunduserid.gefunden,
                        qryF7_GesamtNachtfunduserid.wiedergefunden,
                        qryF7_GesamtNachtfunduserid.geaendert,
                        qryF7_GesamtNachtfunduserid.neueaf,
                        qryF7_GesamtNachtfunduserid.id,
                        tblUserIDundName.geloescht
        FROM qryF7_GesamtNachtfunduserid
        INNER JOIN tblUserIDundName
            ON qryF7_GesamtNachtfunduserid.`userid_und_name_id` = tblUserIDundName.id

        LEFT JOIN qryF8_SE_RechtesucheVorbereiten1
            ON qryF7_GesamtNachtfunduserid.tf = qryF8_SE_RechtesucheVorbereiten1.tf
        WHERE COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
            AND qryF7_GesamtNachtfunduserid.`zi_organisation` NOT LIKE "ai%"
            AND qryF8_SE_RechtesucheVorbereiten1.tf IS NULL
    /*
    ORDER BY tblUserIDundName.name,
             tblUserIDundName.userid,
             qryF7_GesamtNachtfunduserid.tf;
    */
    ;
    ALTER TABLE `RechteDB`.`qryF8_SE_RechteOhneVerwendungInAI` ADD PRIMARY KEY (`id`);

    drop table if exists `tblZZF8_SE-RechtesucheVorbereiten0a`;
    create table `tblZZF8_SE-RechtesucheVorbereiten0a` AS
        SELECT id AS id FROM qryF8_SE_RechteOhneVerwendungInAI;
    ALTER TABLE `RechteDB`.`tblZZF8_SE-RechtesucheVorbereiten0a` ADD PRIMARY KEY (`id`);

    UPDATE `tblZZF8_SE-RechtesucheVorbereiten0a`
    INNER JOIN tblGesamt
        ON `tblZZF8_SE-RechtesucheVorbereiten0a`.id = tblGesamt.id
    SET tblGesamt.`nicht_ai` = TRUE;

END
"""
	return push_sp ('setzeNichtAIFlag', sp, procs_schon_geladen)

def push_sp_macheAFListe(procs_schon_geladen):
	sp = """
CREATE PROCEDURE erzeuge_af_liste()
BEGIN
    /*
        Erzeuge die Liste der erlaubten Arbeitsplatzfunktionen.
        Sie wird später in der Rollenbehandlung benötigt.
    */
    INSERT INTO tbl_AFListe ( `af_name`, neu_ab )
        SELECT `tblUEbersichtAF_GFs`.`name_af_neu` AS af_name, now() AS neu_ab
            FROM tblUEbersichtAF_GFs LEFT JOIN tbl_AFListe ON tblUEbersichtAF_GFs.`name_af_neu` = tbl_AFListe.`af_name`
            WHERE (((tblUEbersichtAF_GFs.modelliert) Is Not Null) AND ((tbl_AFListe.`af_name`) Is Null))
        GROUP BY tblUEbersichtAF_GFs.`name_af_neu`;
END
"""
	return push_sp ('erzeuge_af_liste', sp, procs_schon_geladen)

def push_sp_ueberschreibeModelle(procs_schon_geladen):
	sp = """
CREATE PROCEDURE ueberschreibeModelle()
BEGIN
    /*
        Finde alle Einträge, bei denen ein manuell gesetztes Modell
        nicht zu den aktuell bereits freigegebenen Modell passt.
        Der Fall tritt ein, wenn
        - eine GF/AF-Kombination neut freigegeben wird 
          und diese Kombination ehemals mit einem manuellen Modell versehen worden ist
        - wenn eine Rechteliste neeu eingelesen wird und der Importer versucht, unnötig intelligent zu sein

		In Access heißt die Query qryModellNichtGF_AF.
    */
	CREATE TEMPORARY TABLE auchBloed
	  SELECT 	
	  		tblGesamt.id as diffID,
			tblGesamt.modell as gewaehltes_Modell,
			tblUEbersichtAF_GFs.id as freigegebenes_Modell
	  FROM `tblGesamt`
		INNER JOIN tblUEbersichtAF_GFs
		ON (
			tblUEbersichtAF_GFs.name_af_neu = tblGesamt.enthalten_in_af
			AND tblUEbersichtAF_GFs.name_gf_neu = tblGesamt.gf
		)
	  WHERE tblGesamt.modell <> tblUEbersichtAF_GFs.id;

	UPDATE 	tblGesamt
		INNER JOIN auchBloed
		ON tblGesamt.id = auchBloed.diffID
	SET tblGesamt.modell = auchBloed.freigegebenes_Modell;
END
"""
	return push_sp ('ueberschreibeModelle', sp, procs_schon_geladen)

# Suche nach Stored Procedures in der aktuellen Datenbank
# return: Anzahl an derzeit geladenen Stored Procedures
def anzahl_procs():
	anzahl = 0  # Wenn die Zahl der Einträge bei SHOW > 0 ist, müssen die Procs jeweils gelöscht werden
	with connection.cursor() as cursor:
		try:
			cursor.execute ("show procedure status where db like (select DATABASE())")
			anzahl = cursor.rowcount
		except:
			e = sys.exc_info()[0]
			print('Error in finde_procs(): {}'.format(e))

		cursor.close()
		return anzahl

def finde_procs():
	finde_procs_exakt()
	return anzahl_procs() > 0

def finde_procs_exakt():
	return anzahl_procs() == soll_procs()

sps = {
	1: push_sp_test,
	2: push_sp_vorbereitung,
	3: push_sp_neueUser,
	4: push_sp_behandleUser,
	5: push_sp_behandleRechte,
	6: push_sp_loescheDoppelteRechte,
	7: push_sp_nichtai,
	8: push_sp_macheAFListe,
	9: push_sp_ueberschreibeModelle,
}

def soll_procs():
	return len(sps)

@login_required
def handle_stored_procedures(request):
	# Behandle den Import von Stored-Procedures in die Datenbank
	daten = {}

	if request.method == 'POST':
		procs_schon_geladen = finde_procs()

		daten['anzahl_import_elemente'] = sps[1](procs_schon_geladen)
		daten['call_anzahl_import_elemente'] = call_sp_test()
		daten['vorbereitung'] 			= sps[2](procs_schon_geladen)
		daten['neueUser'] 				= sps[3](procs_schon_geladen)
		daten['behandleUser'] 			= sps[4](procs_schon_geladen)
		daten['behandleRechte'] 		= sps[5](procs_schon_geladen)
		daten['loescheDoppelteRechte'] 	= sps[6](procs_schon_geladen)
		daten['setzeNichtAIFlag'] 		= sps[7](procs_schon_geladen) # Falls die Funktion jemals wieder benötigt wird
		daten['erzeuge_af_liste'] 		= sps[8](procs_schon_geladen)
		daten['ueberschreibeModelle'] 	= sps[9](procs_schon_geladen)

		"""
		daten['anzahl_import_elemente'] = push_sp_test(procs_schon_geladen)
		daten['call_anzahl_import_elemente'] = call_sp_test()
		daten['vorbereitung'] = push_sp_vorbereitung(procs_schon_geladen)
		daten['neueUser'] = push_sp_neueUser(procs_schon_geladen)
		daten['behandleUser'] = push_sp_behandleUser(procs_schon_geladen)
		daten['behandleRechte'] = push_sp_behandleRechte(procs_schon_geladen)
		daten['loescheDoppelteRechte'] = push_sp_loescheDoppelteRechte(procs_schon_geladen)
		daten['setzeNichtAIFlag'] = push_sp_nichtai(procs_schon_geladen) # Falls die Funktion jemals wieder benötigt wird
		daten['erzeuge_af_liste'] = push_sp_macheAFListe(procs_schon_geladen)
		daten['ueberschreibeModelle'] = push_sp_ueberschreibeModelle(procs_schon_geladen)
		"""

	context = {
		'daten': daten,
	}
	return render(request, 'rapp/stored_procedures.html', context)
