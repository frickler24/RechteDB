
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

/*

    Da einige der Importzeilen defekt sind und
    damit der Import und due Ergebnismengen merkwürdig erscheinen,
    hier der Suchstring für den vi:

    /^[\^\d+;]

    Alternativ Suche nach "der Protokolle"
*/

/*

TRUNCATE `tblRechteNeuVonImport`;
LOAD DATA LOCAL INFILE '/tmp/phpbojCHf'     -- ACHTUNG ToDO Die Daten wirklich vom File einlesen
    INSERT INTO TABLE `tblRechteNeuVonImport`
    FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\' LINES TERMINATED BY '\n'
    IGNORE 1 LINES;
*/


-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------
    bis hierhin gehts
-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------------


/*
    ToDo: Historisieren von Rechten gelöschter User (derzeit 86990 insgesamt)

    select tblUserIDundName.Name, tblUserIDundName.userID, tblGesamt.*
    from tblGesamt
    INNER JOIN tblUserIDundName
        ON tblGesamt.`UserID + Name_ID` = tblUserIDundName.ID
    WHERE tblGesamt.`gelöscht` <> FALSE
        AND tblUserIDundName.`gelöscht` = TRUE;



CREATE TEMPORARY TABLE T1 AS
	SELECT ID FROM `tblGesamt` WHERE DATUM > '2018-08-05 20:00:00';

UPDATE 	tblGesamt
	join T1
    on tblGesamt.ID = T1.ID
set tblGesamt.Datum = 0




*/
