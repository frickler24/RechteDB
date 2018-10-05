# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# In dieser Datei sollen die Quellen der Stored-Procedures liegen, die zum DBMS deploed werden

from django.shortcuts import render
from django.db import connection
import sys

from django.shortcuts import get_object_or_404
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.contrib.auth.models import User

from django.urls import reverse_lazy


def push_sp(name, sp):
	# Speichere eine als PArameter übergebene Stored Procedure
	fehler = False
	loeschstring = format ("DROP PROCEDURE IF EXISTS %s" % name)
	with connection.cursor() as cursor:
		try:
			cursor.execute (loeschstring)
			cursor.execute (sp)
		except:
			e = sys.exc_info()[0]
			fehler = format("Error: %s" % e)

		cursor.close()
		return fehler

def push_sp_test():
	sp = """
CREATE PROCEDURE anzahl_import_elemente()
BEGIN
  SELECT COUNT(*) FROM `tblRechteNeuVonImport` ORDER BY `TF Name`, `Identität`;
END
"""
	return push_sp ('anzahl_import_elemente', sp)

def call_sp_test():
	fehler = False
	with connection.cursor() as cursor:
		try:
			cursor.execute ("CALL anzahl_import_elemente")
			liste = cursor.fetchone()
		except:
			e = sys.exc_info()[0]
			fehler = format("Error: %s" % e)

		cursor.close()
		return fehler or not liste[0] >= 0

def push_sp_vorbereitung():
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

        Alternativ Suche nach "der Protokolle"
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
    truncate table qryF3_RechteNeuVonImportDuplikatfrei;
    insert into qryF3_RechteNeuVonImportDuplikatfrei (userid, name, tf, `tf_beschreibung`, 
    			`enthalten_in_af`, `tf_kritikalitaet`,
                `tf_eigentuemer_org`, `tf_technische_plattform`, GF, `vip`, zufallsgenerator,
                `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`, `hk_tf_in_af`,
                `gf_beschreibung`, `af_zuweisungsdatum`)
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
    INSERT INTO tbl_AFListe ( `af_name`, neu_ab )
        SELECT `tblUEbersichtAF_GFs`.`name_af_neu` AS af_name, now() AS neu_ab
            FROM tblUEbersichtAF_GFs LEFT JOIN tbl_AFListe ON tblUEbersichtAF_GFs.`name_af_neu` = tbl_AFListe.`af_name`
            WHERE (((tblUEbersichtAF_GFs.modelliert) Is Not Null) AND ((tbl_AFListe.`af_name`) Is Null))
        GROUP BY tblUEbersichtAF_GFs.`name_af_neu`;


    /*
        Bis hierhin ging die Vorbereitung.
        Die nächsten Schritte müssen manuell und visuell unterstützt werden:
            - Sichtung der neu hinzugekommenen useriden,
            - Übernahme in die userid-Liste
            - Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf geloescht werden sollen
    */
END
"""
	return push_sp ('vorbereitung', sp)

def push_sp_neueUser():
	sp = """
create procedure neueUser (OUT anzahlNeueUser integer(11),
                           OUT anzahlGeloeschteUser integer(11),
                           OUT anzahlGeleseneRechte integer(11),
                           OUT anzahlRechteInAMneu integer(11))
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
        Dieses Statement wird aufgerufen, wenn der "Neue User speichern" Button angeklickt wird.
        Zunächst werden die User in eine temporäre Tabelle geschrieben,
        die in der Importliste auftauchen und
            die nicht in der User-Tabelle auftauchen (die beiden ersten Zeilen im WHERE), oder
            die in der User-Tabelle vorhanden, aber auf "geloescht" gesetzt sind (dritte Zeile im WHERE),
        Der Vergleich erfolgt sowohl über über name als auch userid,
        damit auch erneut vergebene useriden auffallen.

        Gefundene, aber als geloescht markierte User werden reaktiviert,
        die anderen an die vorhandene User-Tabelle angehängt.
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a as
        SELECT DISTINCT tblRechteAMNeu.userid as userid1,
                        tblRechteAMNeu.name as name1,
                        '35' AS Ausdr1,
                        'AI-BA' AS Ausdr2,
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

        ToDo: Mal checken, ob wir die Tabelle wirkjlich materialisiert benötigen oder nicht (evtl. zur Ansicht?)
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a as
    SELECT A.userid, A.name, A.`zi_organisation`
        FROM tblUserIDundName A
        WHERE   A.`zi_organisation` = 'ai-ba'
            AND COALESCE(A.geloescht, FALSE) = FALSE
            AND A.userid not in (select distinct userid from tblRechteAMNeu)
        GROUP BY
            A.userid,
            A.name,
            A.`zi_organisation`
    ;

    -- SELECT * from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;

    -- Ein bisschen Statistik für den Anwender
    select count(*) INTO anzahlNeueUser from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    select count(*) INTO anzahlGeloeschteUser from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    select count(*) INTO anzahlGeleseneRechte from tblRechteNeuVonImport;
    select count(*) INTO anzahlRechteInAMneu from tblRechteAMNeu;

    select 'Anzahl neuer User' as name, count(*) as wert from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a 
    UNION
    select 'Anzahl gelöschter User' as name, count(*) as wert from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
    UNION
    select 'Anzahl gelesener Rechte' as name, count(*) as wert from tblRechteNeuVonImport
    UNION
    select 'Anzahl Rechte in AM_neu' as name, count(*) as wert from tblRechteAMNeu;
    
END
"""
	return push_sp ('neueUser', sp)


def handle_stored_procedures(request):
	# Behandle den Import von Stored-Procedures in die Datenbank
	daten = {}

	print (request.method)
	if request.method == 'POST':
		daten['anzahl_import_elemente'] = push_sp_test()
		daten['call_anzahl_import_elemente'] = call_sp_test()
		daten['vorbereitung'] = push_sp_vorbereitung()
		daten['neueUser'] = push_sp_neueUser()

	context = {
		'daten': daten,
	}
	return render(request, 'rapp/stored_procedures.html', context)

