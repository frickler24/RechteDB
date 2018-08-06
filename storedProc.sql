delimiter //
use RechteDB//
drop procedure vorbereitung//
create procedure vorbereitung()
BEGIN
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
        Seit IIQ werden die wirklichen UserIDen nicht mehr unter der Identität gehalten,
        sondern unter `AF zugewiesen an Account-Name`. Das müssen wir in die UserID
        umkopieren, wo nötig.
    */
    UPDATE tblRechteNeuVonImport
        SET `AF zugewiesen an Account-Name` = `Identität`
    WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-Name` Is Null
        Or tblRechteNeuVonImport.`AF zugewiesen an Account-Name` = "";

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
    truncate table qryF3_RechteNeuVonImportDuplikatfrei;
    insert into qryF3_RechteNeuVonImportDuplikatfrei ()
        SELECT `AF zugewiesen an Account-Name` AS UserID,
               CONCAT(`Nachname`,', ',`Vorname`) AS Name,
               `TF Name` AS TF,
               `TF Beschreibung`,
               `AF Anzeigename` AS `Enthalten in AF`,
               `TF Kritikalität`,
               `TF Eigentümer Org`,
               `TF Applikation` AS `TF Technische Plattform`,
               `GF Name` AS GF,
               'gibt es nicht mehr' AS `VIP Kennzeichen`,
               'gibt es nicht mehr' AS Zufallsgenerator,
               `AF Gültig ab`,
               `AF Gültig bis`,
               `Direct Connect`,
               `Höchste Kritikalität TF in AF`,
               `GF Beschreibung`,
               `AF Zuweisungsdatum`
        FROM tblRechteNeuVonImport
        GROUP BY `UserID`,
                 `TF`,
                 `Enthalten in AF`,
                 `TF Technische Plattform`,
                 `GF`;

    /*
        ALTER TABLE `RechteDB`.`qryF3_RechteNeuVonImportDuplikatfrei`
            ADD PRIMARY KEY (`UserID`, `TF`(70), `Enthalten in AF`(30), `TF Technische Plattform`, `GF`);
    */


    TRUNCATE table tblRechteAMNeu;
    INSERT INTO tblRechteAMNeu (UserID, Name, TF, `TF Beschreibung`, `Enthalten in AF`, `TF Kritikalität`,
                `TF Eigentümer Org`, `TF Technische Plattform`, GF, `VIP Kennzeichen`, Zufallsgenerator,
                `AF Gültig ab`, `AF Gültig bis`, `Direct Connect`, `Höchste Kritikalität TF in AF`,
                `GF Beschreibung`, `AF Zuweisungsdatum`, doppelerkennung)
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
           qryF3_RechteNeuVonImportDuplikatfrei.`AF Zuweisungsdatum`,
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


    /*
        Bis hierhin ging die Vorbereitung.
        Die nächsten Schritte müssen manuell und visuell unterstützt werden:
            - Sichtung der neu hinzugekommenen UserIDen,
            - Übernahme in die UserID-Liste
            - Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf gelöscht werden sollen
    */

END//

drop procedure neueUser//
create procedure neueUser (OUT anzahlNeueUser integer(11),
                           OUT anzahlGeloeschteUser integer(11),
                           OUT anzahlGeleseneRechte integer(11),
                           OUT anzahlRechteInAMneu integer(11))
BEGIN

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


    /*
        Dieses Statement wird aufgerufen, wenn der "Neue User speichern" Button angeklickt wird.
        Zunächst werden die User in eine temporäre Tabelle geschrieben,
        die in der Importliste auftauchen und
            die nicht in der User-Tabelle auftauchen (die beiden ersten Zeilen im WHERE), oder
            die in der User-Tabelle vorhanden, aber auf "gelöscht" gesetzt sind (dritte Zeile im WHERE),
        Der Vergleich erfolgt sowohl über über Name als auch UserID,
        damit auch erneut vergebene UserIDen auffallen.

        Gefundene, aber als gelöscht markierte User werden reaktiviert,
        die anderen an die vorhandene User-Tabelle angehängt.
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a as
        SELECT DISTINCT tblRechteAMNeu.UserID as UserID1,
                        tblRechteAMNeu.Name as Name1,
                        '35' AS Ausdr1,
                        'AI-BA' AS Ausdr2,
                        tblUserIDundName.UserID as UserID2,
                        tblUserIDundName.Name as Name2,
                        tblUserIDundName.gelöscht
        FROM tblRechteAMNeu
            LEFT JOIN tblUserIDundName
            ON tblRechteAMNeu.UserID = tblUserIDundName.UserID
            AND tblUserIDundName.Name = tblRechteAMNeu.Name

        WHERE (tblRechteAMNeu.UserID    IS NOT NULL AND tblUserIDundName.UserID IS NULL)
            OR (tblRechteAMNeu.Name     IS NOT NULL AND tblUserIDundName.Name   IS NULL)
            OR tblUserIDundName.`gelöscht` = TRUE;

    /*
        Sichtung der nicht mehr vorhandenen User, deren Einträge im weiteren Verlauf gelöscht werden sollen
        Erst einmal werden die Rechte der als zu löschen markierten User in die Historientabelle verschoben.

        ToDo: Mal checken, ob wir die Tabelle wirkjlich materialisiert benötigen oder nicht (evtl. zur Ansicht?)
    */

    drop table if exists qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    create table qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a as
    SELECT A.UserID, A.Name, A.`ZI-Organisation`
        FROM tblUserIDundName A
        WHERE   A.`ZI-Organisation` = 'ai-ba'
            AND COALESCE(A.gelöscht, FALSE) = FALSE
            AND A.UserID not in (select distinct userid from tblRechteAMNeu)
        GROUP BY
            A.UserID,
            A.Name,
            A.`ZI-Organisation`
    ;

    -- SELECT * from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;

    -- Ein bisschen Statistik für den Anwender
    select count(*) INTO anzahlNeueUser from qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a;
    select count(*) INTO anzahlGeloeschteUser from qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a;
    select count(*) INTO anzahlGeleseneRechte from tblRechteNeuVonImport;
    select count(*) INTO anzahlRechteInAMneu from tblRechteAMNeu;

END//

delimiter //
drop procedure behandleUser//
create procedure behandleUser ()
BEGIN

    create temporary table tbl_tmpGeloeschte as
        SELECT UserID1
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
            WHERE `gelöscht` = True;

    -- select * from tbl_tmpGeloeschte;

    /*
        Markiere die UserIDen wieder als aktiv, die bereits bekannt, aber als gelöscht markiert sind.
    */
    UPDATE tblUserIDundName
        INNER JOIN tbl_tmpGeloeschte
            ON tbl_tmpGeloeschte.UserID1 = tblUserIDundName.UserID
    SET tblUserIDundName.gelöscht = False;

    /*
        Nun werden die wirklich neuen User an die UserID-Tabelle angehängt
        qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a2 u.a.
    * /
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
    */
    INSERT INTO tblUserIDundName (UserID, Name, Orga_ID, `ZI-Organisation` )
        SELECT UserID1, Name1, Ausdr1 AS Orga_ID, Ausdr2 AS `ZI-Organisation`
            FROM qryUpdateNeueBerechtigungenZIAIBA_1_NeueUser_a
            WHERE COALESCE(`gelöscht`, FALSE) = FALSE
                AND (UserID1 IS NOT NULL OR Name1 IS NOT NULL);


    -- select * from tblUserIDundName;


    /*
        Bevor die alten User als gelöscht markiert werden,
        müssen deren derzeit vorhandenen Rechte in die Historientabelle verschoben werden.
    */

    INSERT INTO tblGesamtHistorieNeu (
                `UserID + Name_ID`, TF, `TF Beschreibung`, `Enthalten in AF`,
                Modell, `TF Kritikalität`, `TF Eigentümer Org`, `AF Zuweisungsdatum`,
                Plattform_ID, GF, gelöscht, gefunden, wiedergefunden, geändert, löschdatum, NeueAF, Datum, `ID-alt`
            )
    SELECT `tblGesamt`.`UserID + Name_ID`,
           `tblGesamt`.TF,
           `tblGesamt`.`TF Beschreibung`,
           `tblGesamt`.`Enthalten in AF`,
           `tblGesamt`.Modell,
           `tblGesamt`.`TF Kritikalität`,
           `tblGesamt`.`TF Eigentümer Org`,
           `tblGesamt`.`AF Zuweisungsdatum`,
           `tblGesamt`.Plattform_ID,
           `tblGesamt`.GF,
           `tblGesamt`.`gelöscht`,
           `tblGesamt`.gefunden,
           `tblGesamt`.wiedergefunden,
           `tblGesamt`.`geändert`,
           Now() AS Ausdr1,
           `tblGesamt`.NeueAF,
           `tblGesamt`.Datum,
           `tblGesamt`.ID
        FROM `tblGesamt`
        INNER JOIN (tblUserIDundName
                    inner join qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
                    on qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.UserID = tblUserIDundName.UserID)
            ON tblUserIDundName.ID = `tblGesamt`.`UserID + Name_ID`
        WHERE tblUserIDundName.UserID IN (SELECT UserID FROM `qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a`)
            AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE;


    -- Setzen der Löschflags in der Gesamttabelle für jedes Recht jeder nicht mehr vorhandenen UserID

    UPDATE
        tblGesamt
        INNER JOIN (tblUserIDundName
                    inner join qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
                    on qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.UserID = tblUserIDundName.UserID)
	        ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
        SET tblGesamt.gelöscht = TRUE,
            tblGesamt.`löschdatum` = Now()
        WHERE COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE;

    -- Die User werden in der User-Tabelle nun auf "gelöscht" gesetzt

    UPDATE tblUserIDundName
        inner join qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a
            on qryUpdateNeueBerechtigungenZIAIBA_2_GelöschteUser_a.UserID = tblUserIDundName.UserID
        SET `gelöscht` = TRUE
        WHERE COALESCE(`gelöscht`, FALSE) = FALSE;

    -- ToDo Es fehlt komplett das Löschen der historisierten Rechte für gerade gelöschte User

END//

-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------

delimiter //
drop procedure behandleRechte//
create procedure behandleRechte ()
BEGIN

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

    UPDATE tblGesamt
        INNER JOIN tblUserIDundName
        ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
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

        ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller UserIDs benötigt wird, sonst löschen nach Nutzung
    */

    drop table if exists tbl_Gesamt_komplett;
    create table tbl_Gesamt_komplett as
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

        WHERE COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
            AND tblUserIDundName.UserID in (select distinct userid from tblRechteAMNeu)
        ORDER BY tblGesamt.TF,
                 tblUserIDundName.UserID;

    /*
        Markieren der Flags Gefunden in tblRechteAMNeu sowie tblGesamt.
        In letzterer wird auch das Datum eingetragen, wann das Recht wiedergefunden wurde.

        Zusätzlich werden alle Felder, die hier nicht zum Vergleich der Rechte-Gleichheit
        genutzt wurden, in der Gesamttabelle aktualisiert.

        Das hat früher mal zu Problemen geführt, in letzter Zeit aber eher nicht mehr.

    */

    -- Zunächst das Setzen und Kopieren der Daten im Fall "Wiedergefunden"
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

    WHERE COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
        AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE;


    /*
        qryF2setzeGeaentderteAlteAF implementiert den Fall der geänderten AF aber ansonsten gleichen Daten
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
        AND COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
        AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE
        ;

    /*
        qryF5c_HistorisiereGeaenderteEintraege
        In die Historientabelle werden die zur Änderung vorgemerkten Einträge aus der Gesamttabelle kopiert.
    */

    INSERT INTO tblGesamtHistorieNeu (`UserID + Name_ID`, TF, `TF Beschreibung`, `Enthalten in AF`, Modell, `TF Kritikalität`,
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
           AND tblUserIDundName.`ZI-Organisation` LIKE 'AI-BA';      -- ToDo: Wird die Einschränkung wirklich benötigt?
           -- ToDo: Es sollte ja nicht kopiert, sondern verschoben werden. Es fehlt hier also das Löschen.


    /*
        Anschließend können die geänderten Werte in die GesamtTabelle übernommen werden.
        Dazu wird der Inhalt des Kommentarfelds in die AF-alt-Spalte eingetragen.
        Damit müsste das erledigt sein :-)

        qryF5d_AktualisiereGeaenderteAF
    */

    -- ToDo: Später noch mal das geändert-Flag zurücksetzen, dann entfällt das ToDo vorher...

    UPDATE tblUserIDundName
        INNER JOIN tblGesamt
        ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`
    SET tblGesamt.`Enthalten in AF` = `NeueAF`

    WHERE tblGesamt.`geändert` = TRUE
        AND tblUserIDundName.`ZI-Organisation` = 'AI-BA';


    /*
        Als nächstes kann es sein, dass in der Importliste noch TF mit NEUEN AF stehen,
        die zwar bereits in der Gesamtliste bezogen auf die UID bekannt sind,
        dort aber bereits mit den ALTEN AF-Bezeichnungen gefunden wurden.
        Damit nun nicht bei jedem wiederholten Import die AF-Bezeichnungen umgeschossen werden,
        hängen wir diese Zeilen nun hinten an die Gesamttabelle an.

        Dazu werden im ersten Schritt in der Importtabelle die Zeilen markiert (angehaengtBekannt),
        die anzuhängen sind. Das sieht zwar umständlich aus, erleichtert aber später die Bewertung.
        ob noch irgendwelche Einträge in der Importtabelle nicht bearbeitet wurden.
        Die Flags kann man eigentlich auch zusammenfassen,
        dann müssten aber bearbeitete Zeilen separat umgeschossen werden...

        Beim Einfügen der neuen TF-AF-Kombinationen wird in der Gesamttabelle "gefunden" gesetzt,
        damit das Recht später nicht gleich wieder gelöscht wird.

        ToDo: Eigentlich müssten hierbei auch die GF berüchsichtigt werden - da gab es aber noch keine Auffälligkeiten

        qryF5_FlaggeTFmitNeuenAFinImportTabelle
    */

    UPDATE tblRechteAMNeu
        INNER JOIN tbl_Gesamt_komplett
        ON (tbl_Gesamt_komplett.Zufallsgenerator = tblRechteAMNeu.Zufallsgenerator)
            AND (tbl_Gesamt_komplett.`VIP Kennzeichen` = tblRechteAMNeu.`VIP Kennzeichen`)
            AND (tblRechteAMNeu.GF = tbl_Gesamt_komplett.GF)
            AND (tblRechteAMNeu.`Enthalten in AF` = tbl_Gesamt_komplett.`Enthalten in AF`)
            AND (tblRechteAMNeu.UserID = tbl_Gesamt_komplett.UserID)
            AND (tblRechteAMNeu.TF = tbl_Gesamt_komplett.TF)
            AND (tblRechteAMNeu.`TF Technische Plattform` = tbl_Gesamt_komplett.`TF Technische Plattform`)
        SET tblRechteAMNeu.`angehängtBekannt` = TRUE
        WHERE tblRechteAMNeu.Gefunden = TRUE
            AND tblRechteAMNeu.`Geändert` = FALSE;

    /*
        Zum Gucken:

    SELECT COUNT(*) FROM tblRechteAMNeu
        INNER JOIN tbl_Gesamt_komplett
        ON (tbl_Gesamt_komplett.Zufallsgenerator = tblRechteAMNeu.Zufallsgenerator)
            AND (tbl_Gesamt_komplett.`VIP Kennzeichen` = tblRechteAMNeu.`VIP Kennzeichen`)
            AND (tblRechteAMNeu.GF = tbl_Gesamt_komplett.GF)
            AND (tblRechteAMNeu.`Enthalten in AF` = tbl_Gesamt_komplett.`Enthalten in AF`)
            AND (tblRechteAMNeu.UserID = tbl_Gesamt_komplett.UserID)
            AND (tblRechteAMNeu.TF = tbl_Gesamt_komplett.TF)
            AND (tblRechteAMNeu.`TF Technische Plattform` = tbl_Gesamt_komplett.`TF Technische Plattform`)
        WHERE tblRechteAMNeu.Gefunden = TRUE
            AND tblRechteAMNeu.`Geändert` = FALSE;
    */

    /*
        Anschließend werden diese selektierten Zeilen an die Gesamttabelle angehängt.
        Dabei wird in der Gesamttabelle das Flag "gefunden" gesetzt,
        um diese Einträge erkennbar zu machen für das nachfolgende Löschen alter Einträge.

        qryF5_HaengeTFmitNeuenAFanGesamtTabelleAn
    */

    INSERT INTO tblGesamt (TF, `TF Beschreibung`, `Enthalten in AF`, Datum, Modell, `UserID + Name_ID`,
                Plattform_ID, Gefunden, `geändert`, `TF Kritikalität`, `TF Eigentümer Org`, GF, `VIP Kennzeichen`,
                Zufallsgenerator, `AF Gültig ab`, `AF Gültig bis`, `Direct Connect`, `Höchste Kritikalität TF in AF`,
                `GF Beschreibung`, `AF Zuweisungsdatum`)
    SELECT  tblRechteAMNeu.TF,
            tblRechteAMNeu.`TF Beschreibung`,
            tblRechteAMNeu.`Enthalten in AF`,
            Now() AS DatumNeu,
            (
                SELECT DISTINCT Modell
                FROM `tblGesamt`
                WHERE `tblGesamt`.`UserID + Name_ID` = (
                    SELECT DISTINCT ID
                    FROM tblUserIDundName
                    WHERE UserID = tblRechteAMNeu.UserID
                )
                AND `tblGesamt`.`TF` = `tblRechteAMNeu`.`TF`
                LIMIT 1
            ) AS ModellNeu,

            (SELECT ID FROM tblUserIDundName WHERE UserID = tblRechteAMNeu.UserID) AS UIDNameNeu,

            (SELECT ID FROM tblPlattform
                WHERE `TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`) AS PlattformNeu,
            TRUE AS Ausdr1,
            tblRechteAMNeu.`geändert`,
            tblRechteAMNeu.`TF Kritikalität`,
            tblRechteAMNeu.`TF Eigentümer Org`,
            tblRechteAMNeu.GF,
            tblRechteAMNeu.`VIP Kennzeichen`,
            tblRechteAMNeu.Zufallsgenerator,
            tblRechteAMNeu.`AF Gültig ab`,
            tblRechteAMNeu.`AF Gültig bis`,
            tblRechteAMNeu.`Direct Connect`,
            tblRechteAMNeu.`Höchste Kritikalität TF in AF`,
            tblRechteAMNeu.`GF Beschreibung`,
            tblRechteAMNeu.`AF Zuweisungsdatum`

    FROM tblRechteAMNeu
    WHERE tblRechteAMNeu.Gefunden = FALSE
        AND tblRechteAMNeu.`angehängtBekannt` = TRUE;

    /*
        Nun werden noch die Rechte derjenigen User behandelt,
        die bislang in der Importtabelle nicht berücksichtigt worden sind.
        Dies können nur noch Rechte bislang unbekannter User
        oder unbekannte Rechte bekannter User sein.
        Dazu werden diese Rechte zunächst mit dem Flag "angehaengtSonst" markiert:

        qryF5_FlaggeTFmitNeuenAFinImportTabelleUnbekannteUser
    */


    UPDATE tblRechteAMNeu
    SET `angehängtSonst` = TRUE
    WHERE Gefunden = FALSE
        AND `Geändert` = FALSE
        AND `angehängtBekannt` = FALSE;

    /*
    select * from tblRechteAMNeu
    WHERE Gefunden = FALSE
        AND `Geändert` = FALSE
        AND `angehängtBekannt` = FALSE;
    */

    /*
        Jetzt sehen wir uns die Plattform an, die in der Importliste auftauchen
        und hängen gegebenenfalls fehlende Einträge an die Plattform-Tabelle an.

        qryF5_AktualisierePlattformListe
    */

    INSERT INTO tblPlattform (`TF Technische Plattform`)
    SELECT DISTINCT tblRechteAMNeu.`TF Technische Plattform`
    FROM tblRechteAMNeu
        LEFT JOIN tblPlattform
        ON tblRechteAMNeu.`TF Technische Plattform` = tblPlattform.`TF Technische Plattform`
        WHERE tblPlattform.`TF Technische Plattform` IS NULL;


    /*
        Nun werden alle neuen Rechte aller User an die Gesamttabelle angehängt.
        Der alte query-Name weist irrtümlich darauf hin, dass nur neue User hier behandelt würden,
        das ist aber definitiv nicht so.

        qryF5_HaengeTFvonNeuenUsernAnGesamtTabelleAn
    */

    INSERT INTO tblGesamt (TF, `TF Beschreibung`, `Enthalten in AF`, Datum, Modell, `UserID + Name_ID`,
                Plattform_ID, Gefunden, `Geändert`, `TF Kritikalität`, `TF Eigentümer Org`, gelöscht, GF,
                `VIP Kennzeichen`, Zufallsgenerator, `AF Gültig ab`, `AF Gültig bis`, `Direct Connect`,
                `Höchste Kritikalität TF in AF`, `GF Beschreibung`, `AF Zuweisungsdatum`)
    SELECT  tblRechteAMNeu.TF,
            tblRechteAMNeu.`TF Beschreibung`,
            tblRechteAMNeu.`Enthalten in AF`,
            Now() AS DatumNeu,

            (SELECT `id` FROM `tblÜbersichtAF_GFs` WHERE `Name AF Neu` LIKE 'Neues Recht noch nicht eingruppiert') AS ModellNeu,

            (SELECT ID FROM tblUserIDundName WHERE UserID = tblRechteAMNeu.UserID) AS UIDNameNeu,

            (SELECT ID FROM tblPlattform
                WHERE `TF Technische Plattform` = tblRechteAMNeu.`TF Technische Plattform`) AS PlattformNeu,

            TRUE AS Ausdr1,
            FALSE AS Ausdr2,
            tblRechteAMNeu.`TF Kritikalität`,
            tblRechteAMNeu.`TF Eigentümer Org`,
            FALSE AS Ausdr3,
            tblRechteAMNeu.GF,
            tblRechteAMNeu.`VIP Kennzeichen`,
            tblRechteAMNeu.Zufallsgenerator,
            tblRechteAMNeu.`AF Gültig ab`,
            tblRechteAMNeu.`AF Gültig bis`,
            tblRechteAMNeu.`Direct Connect`,
            tblRechteAMNeu.`Höchste Kritikalität TF in AF`,
            tblRechteAMNeu.`GF Beschreibung`,
            tblRechteAMNeu.`AF Zuweisungsdatum`
    FROM tblRechteAMNeu
    WHERE tblRechteAMNeu.`angehängtSonst` = TRUE;


    /*
        Importiert und angehängt haben wir alles.
        Was noch fehlt, ist das Markieren derjenigen Einträge,
        die bislang bekannt waren, aber in der Importtabelle nicht mehr auftauchen.

        Dabei handelt es sich um gelöschte Rechte oder gelöschte User.

        Um die Nachvollziehbarkeit erhalten zu können,
        wird in der nachfolgenden Abfrage nur das "gelöscht"-Flag gesetzt, aber kein Eintrag entfernt.
        Da wir nicht wissen, ab wann das Element gelöscht wurde,
        sondern wir nur den Tagesstand des Importabzugs kennen, wird ein separates Löschdatum gesetzt.
        Damit bleiben im Datensatz das Einstellungsdatum und das letzte Wiederfinde-Datum erhalten, das muss reichen.

        Die Abfrage greift nur auf TFs von Usern zurück, die sich auch in der Importtabelle befinden
        (sonst würden u.U. Rechte von anderen User ebenfalls auf "gelöscht" gesetzt).
        Das führt dazu, dass TFs von nicht mehr existenten Usern hiervon nicht markiert werden.
        Dazu gibt es aber die Funktion "gelöschte User entfernen", die vorher genutzt wurde.

        qryF8_SetzeLoeschFlagInGesamtTabelle
    */

    UPDATE tblUserIDundName
        INNER JOIN tblGesamt
        ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`
            AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE
            AND COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
            AND COALESCE(tblGesamt.gefunden, FALSE) = FALSE
            AND COALESCE(tblGesamt.`geändert`, FALSE) = FALSE
            AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE

    SET tblGesamt.gelöscht = TRUE,
        tblGesamt.löschdatum = Now()

    WHERE tblUserIDundName.UserID IN (SELECT `UserID` FROM `tblRechteAMNeu` WHERE `UserID` = `tblUserIDundName`.`UserID`);


    /*
        Dann werden noch die Standardwerte für die rvm_ und RVA_00005 Einträge auf "Bleibt (Control-SA)" gesetzt,
        denn das ist Vorgabe von BM.

        Was eigentlich auch automatisch gesetzt werden sollte, sind die rvo_ Rechte,
        aber die sind extrem fehlerhaft modelliert.
        Deshalb lassen wir bis auf das AI-Recht erst mal die Finger davon.

        qryF5_AktualisiereRVM_

        qryF5_AktualisiereRVO_00005 wurde nicht mit übernommen,
        weil die rvo_Rechte nun in der neuen Modellierung berücksichtigt werden
    */

    UPDATE tblGesamt,
           tblÜbersichtAF_GFs
    SET tblGesamt.Modell = `tblÜbersichtAF_GFs`.`ID`
    WHERE tblGesamt.`Enthalten in AF` LIKE "rvm_*"
        AND tblÜbersichtAF_GFs.`Name GF Neu` = "Bleibt (Control-SA)"
        AND COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE;


    /*
        Das Flag, ob ein Recht sich auf einen AI-User bezieht, wird korrigiert

        qryF8_SE_RechtesucheVorbereiten0

        ToDo: Keine Ahnung mehr, wozu das Nicht-AI-Flag gedient hat. Prüfung und ggfs. enfernen. Die Suchabfrage scheint auch kompletter Unfug zu sein.
    */

    UPDATE tblGesamt
        INNER JOIN tblUserIDundName
        ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
        AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE
        AND COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE

    SET tblGesamt.`Nicht AI` = FALSE

    WHERE tblGesamt.`Nicht AI` = TRUE
        AND tblUserIDundName.UserID IN (SELECT DISTINCT tblRechteAMNeu.UserID FROM tblRechteAMNeu);

    /*
        Die nächsten vier temporären Tabellen dienen einem einzigen Zweck:

        Für alle derzeit betrachteten Rechte wird in der Gesamttabelle festgehalten,
        welche für AI sind und welche nicht.

        Das wurde wohl früher mal für SE-Modellierungen genutzt.

        Dazu werden die folgenden temporären Queries erzeugt:

        qryF7_GesamtNachTFundUserID:   Enthält "eigentlich" alle Daten zur ordentlichen Anzeige.
            Dem Namen nach müssten die Daten genau so sortiert sein wie angegeben,
            aber in unserem Fall hier kostet das nur Laufzeit und wird hier nicht benötigt.

        ToDo: Ein paar Daten-Fehler hierbei...

        / *
        -------------
        Suchstring nach 6 verlorenen Rechten


        select tblGesamt.id as gesamtID, qryF7_GesamtNachTFundUserID.id as tmpID
        from tblGesamt
        left join qryF7_GesamtNachTFundUserID
            on tblGesamt.id = qryF7_GesamtNachTFundUserID.id
        where tblGesamt.gelöscht = False
        AND qryF7_GesamtNachTFundUserID.id is null


        Abweichung sind 6 Rechte, die durch die Joins verschwinden:
        00000402897, 00000402898, 00000402899, 00000402900, 00000402901, 00000402902
        * /


        ToDO Löschen der Query nach Prüfung
    */


    -- qryF7_GesamtNachTFundUserID liefert eine Rechteliste der aktiven User aus der Gesamttabelle
    drop table if exists qryF7_GesamtNachTFundUserID;
    create table qryF7_GesamtNachTFundUserID AS
        SELECT tblOrga.`intern - extern`,
               tblGesamt.ID,
               tblGesamt.TF,
               tblGesamt.`UserID + Name_ID`,
               tblGesamt.`TF Beschreibung`,
               tblGesamt.`Enthalten in AF`,
               tblGesamt.Modell,
               tblGesamt.`TF Kritikalität`,
               tblGesamt.`TF Eigentümer Org`,
               tblGesamt.Plattform_ID,
               tblUserIDundName.`ZI-Organisation`,
               tblGesamt.Datum,
               tblGesamt.gefunden,
               tblGesamt.wiedergefunden,
               tblGesamt.geändert,
               tblGesamt.NeueAF,
               tblGesamt.`Nicht AI`

        FROM tblGesamt
            INNER JOIN tblÜbersichtAF_GFs
                ON tblGesamt.Modell = tblÜbersichtAF_GFs.ID

            INNER JOIN tblPlattform
                ON tblGesamt.Plattform_ID = tblPlattform.ID

            INNER JOIN (tblUserIDundName INNER JOIN tblOrga ON tblUserIDundName.Orga_ID = tblOrga.ID)
                ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID

        WHERE COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
            AND COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE

        -- ORDER BY tblGesamt.TF, tblGesamt.`UserID + Name_ID`
    ;
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachTFundUserID` ADD PRIMARY KEY (`ID`);
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachTFundUserID` ADD KEY TF (`TF`);
    ALTER TABLE `RechteDB`.`qryF7_GesamtNachTFundUserID` ADD KEY UserID (`UserID + Name_ID`);


    -- qryF8_SE_RechtesucheVorbereiten1 liefert alle TFen distinct, die bei Usern von AI verwendet werden
    drop table if exists qryF8_SE_RechtesucheVorbereiten1;
    create table qryF8_SE_RechtesucheVorbereiten1 AS
        SELECT distinct tblGesamt.TF
        FROM tblUserIDundName
        INNER JOIN tblGesamt
            ON tblUserIDundName.ID = tblGesamt.`UserID + Name_ID`

        WHERE COALESCE(tblGesamt.`gelöscht`, FALSE) = FALSE
            AND tblUserIDundName.`ZI-Organisation` LIKE "ai%";
    ALTER TABLE `RechteDB`.`qryF8_SE_RechtesucheVorbereiten1` ADD PRIMARY KEY (`TF`);

    -- Nun wird eine Liste mit Rechten zusammengestellt,
    -- die nicht von AI sind.
    -- ToDo: Gruseliges SQL entwirren

    drop table if exists qryF8_SE_RechteOhneVerwendungInAI;
    create table qryF8_SE_RechteOhneVerwendungInAI AS
        SELECT DISTINCT tblUserIDundName.Name,
                        tblUserIDundName.UserID,
                        qryF7_GesamtNachTFundUserID.TF,
                        qryF7_GesamtNachTFundUserID.`TF Beschreibung`,
                        qryF7_GesamtNachTFundUserID.`Enthalten in AF`,
                        qryF7_GesamtNachTFundUserID.Modell,
                        qryF7_GesamtNachTFundUserID.`TF Kritikalität`,
                        qryF7_GesamtNachTFundUserID.`TF Eigentümer Org`,
                        qryF7_GesamtNachTFundUserID.Plattform_ID,
                        qryF7_GesamtNachTFundUserID.Datum,
                        qryF7_GesamtNachTFundUserID.gefunden,
                        qryF7_GesamtNachTFundUserID.wiedergefunden,
                        qryF7_GesamtNachTFundUserID.geändert,
                        qryF7_GesamtNachTFundUserID.NeueAF,
                        qryF7_GesamtNachTFundUserID.ID,
                        tblUserIDundName.gelöscht
        FROM qryF7_GesamtNachTFundUserID
        INNER JOIN tblUserIDundName
            ON qryF7_GesamtNachTFundUserID.`UserID + Name_ID` = tblUserIDundName.ID

        LEFT JOIN qryF8_SE_RechtesucheVorbereiten1
            ON qryF7_GesamtNachTFundUserID.TF = qryF8_SE_RechtesucheVorbereiten1.TF
        WHERE COALESCE(tblUserIDundName.`gelöscht`, FALSE) = FALSE
            AND qryF7_GesamtNachTFundUserID.`ZI-Organisation` NOT LIKE "ai%"
            AND qryF8_SE_RechtesucheVorbereiten1.TF IS NULL
    /*
    ORDER BY tblUserIDundName.Name,
             tblUserIDundName.UserID,
             qryF7_GesamtNachTFundUserID.TF;
    */
    ;
    ALTER TABLE `RechteDB`.`qryF8_SE_RechteOhneVerwendungInAI` ADD PRIMARY KEY (`ID`);

    drop table if exists `tblZZF8_SE-RechtesucheVorbereiten0a`;
    create table `tblZZF8_SE-RechtesucheVorbereiten0a` AS
        SELECT ID AS ID FROM qryF8_SE_RechteOhneVerwendungInAI;
    ALTER TABLE `RechteDB`.`tblZZF8_SE-RechtesucheVorbereiten0a` ADD PRIMARY KEY (`ID`);

    UPDATE `tblZZF8_SE-RechtesucheVorbereiten0a`
    INNER JOIN tblGesamt
        ON `tblZZF8_SE-RechtesucheVorbereiten0a`.ID = tblGesamt.ID
    SET tblGesamt.`Nicht AI` = TRUE;


    /*
        Jetzt müssen zum Abschluss noch in denjenigen importierten Zeilen,
        bei denen die TFs unbekannt sind, das Modell auf "neues Recht" gesetzt werden.
        Die sind daran zu erkennen, dass das Modell NULL ist.
    */

    UPDATE tblGesamt,
           tblÜbersichtAF_GFs
    SET tblGesamt.Modell = `tblÜbersichtAF_GFs`.`ID`
    WHERE tblÜbersichtAF_GFs.`Name GF Neu` = "Neues Recht noch nicht eingruppiert"
       AND tblGesamt.Modell IS NULL;


/*
    Und fertig wir sind.
*/
END//

-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------

delimiter //
drop procedure loescheDoppelteRechte//
create procedure loescheDoppelteRechte (IN nurLesen bool)
BEGIN
    /*
        Prozedur zum Finden und Löschen doppelt vorhandener Einträge in der Gesamttabelle.
        Auch wenn das eigentlich ie vorkommen dürfte, passiert das dennoch ab und an.
        Hauptgruind sind falsch formatierte Eingatelisten.
    */

    CREATE temporary table qryF3_DoppelteElementeFilterAusGesamtTabelle as
        SELECT b.ID,
            b.TF,
            a.gelöscht as RechtGeloescht,
            b.gelöscht as UserGeloescht,
            tblUserIDundName.UserID,
            tblUserIDundName.Name,
            a.GF,
            a.`VIP Kennzeichen`,
            a.Zufallsgenerator

            FROM tblGesamt AS b,
                tblUserIDundName
                INNER JOIN tblGesamt AS a
                    ON tblUserIDundName.ID = a.`UserID + Name_ID`
            WHERE `a`.id < `b`.`id`
                AND COALESCE(a.gelöscht, FALSE) = FALSE
                AND COALESCE(`a`.gelöscht, FALSE) = FALSE
                AND `a`.GF = `b`.`gf`
                AND `a`.`VIP Kennzeichen` = `b`.`VIP Kennzeichen`
                AND `a`.Zufallsgenerator = `b`.`Zufallsgenerator`
                AND `a`.`UserID + Name_ID`=`b`.`UserID + Name_ID`
                AND `a`.TF = `b`.`TF`
                AND `a`.`Enthalten in AF` = `b`.`Enthalten in AF`
                AND `a`.`TF Beschreibung` = `b`.`TF Beschreibung`
                AND `a`.Plattform_ID = `b`.`Plattform_ID`
                AND `a`.`TF Kritikalität` = `b`.`TF Kritikalität`
                AND `a`.`TF Eigentümer Org` = `b`.`TF Eigentümer Org`;

    IF (COALESCE(nurlesen, false) = True)
    THEN
        select count(*) from qryF3_DoppelteElementeFilterAusGesamtTabelle;
    ELSE
        UPDATE tblGesamt
            SET tblGesamt.gelöscht = True,
            tblGesamt.Patchdatum = Now()
            WHERE COALESCE(tblGesamt.gelöscht, FALSE) = False
                AND tblGesamt.ID In (SELECT ID FROM qryF3_DoppelteElementeFilterAusGesamtTabelle GROUP BY ID);
    END IF;
END//

-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- ---------Hier ein paar Testcalls zum Import der Daten -------------------------------
-- ---------Und Bereinigen doppelter Einträge.------------------------------------------
-- -------------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------------
-- ToDo: Die Anpassung der Modelle an genehmigte AV/GF-Kobinationen muss noch eingebaut werden
-- ToDo: temporär genutzte Tabellen entsorgen
-- ToDo: Notieren, welche Tabellen wirklich genutzt werden

delimiter ;

use RechteDB;
call vorbereitung();
call neueUser(@neue, @gelöschte, @gelesene, @inAMneu);
select @neue as 'Anzahl neuer User', @gelöschte as 'Anzahl zu löschender User',
        @gelesene as 'Zeile in Eingabetabelle', @inAMneu as 'Zu verarbeitende Zeilen';

call behandleUser();
call neueUser(@neue, @gelöschte, @gelesene, @inAMneu);
select @neue as 'Anzahl neuer User', @gelöschte as 'Anzahl zu löschender User',
        @gelesene as 'Zeile in Eingabetabelle', @inAMneu as 'Zu verarbeitende Zeilen';

call behandleRechte();
call loescheDoppelteRechte(false);

select count(*)
from tblGesamt
    join tblUserIDundName
        on tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
    WHERE COALESCE(tblGesamt.`gelöscht`, false) = false
    	AND COALESCE(tblUserIDundName.`gelöscht`, false) = false
        AND tblUserIDundName.`ZI-Organisation` = 'AI-BA'
;




