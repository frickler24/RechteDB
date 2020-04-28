-- -----------------------------------------------------
-- -----------------------------------------------------
-- -----------------------------------------------------
--
-- Aktualisiere Spezialrollen für Technische User
--
-- -----------------------------------------------------
-- -----------------------------------------------------
-- -----------------------------------------------------

--
-- Erzeuge neue Rollen für neue Technische User
-- Diese Rollen sind dann erst einmal "leer", haben also keine AFs zugeordnet.
-- Die Länge der Rollennamen wird auf 90 begrenzt,
-- damit ist noch Platz für 10 UTF-Sonderzeichen > 1Byte
--

USE RechteDB;

BEGIN;
    SELECT COUNT(*) as "Anzahl Rollen bei Transaktionsstart" FROM tbl_Rollen;
    INSERT INTO tbl_Rollen
        SELECT LEFT(concat("Technischer User: ", tblUserIDundName.name), 90) AS `rollenname`,
                    "Technischer User" AS `system`,
                    "" AS `rollenbeschreibung`,
                    now() AS `datum`
                    FROM `tblUserIDundName`
                    LEFT JOIN tbl_Rollen
            ON concat("Technischer User: ", tblUserIDundName.name) = tbl_Rollen.rollenname

        WHERE
            tblUserIDundName.userid like "xv86%"
                AND tblUserIDundName.zi_organisation = "ai-xa"
                AND NOT tblUserIDundName.geloescht
                AND tbl_Rollen.rollenname is null

        ORDER BY tblUserIDundName.name
    ON DUPLICATE KEY UPDATE tbl_Rollen.`datum` = now()
    ;

    SELECT COUNT(*) as "Anzahl Rollen nach Erzeugung" FROM tbl_Rollen;

    --
    -- Finde die AF je Technischem User
    --
    DROP TABLE IF EXISTS patchTU_alleAF;
    CREATE TABLE patchTU_alleAF
    SELECT DISTINCT LEFT(concat("Technischer User: ", tblUserIDundName.name), 90) AS `rollenname`,
        tblUserIDundName.userid, tblUserIDundName.name,
        tblGesamt.enthalten_in_af,
        tbl_AFListe.id as af
    FROM tblGesamt
        INNER JOIN `tblUserIDundName`
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
        LEFT JOIN tbl_AFListe
        ON tblGesamt.enthalten_in_af = tbl_AFListe.af_name
    WHERE
        tblUserIDundName.userid like "xv86%"
            AND tblUserIDundName.zi_organisation = "ai-xa"
            AND NOT tblUserIDundName.geloescht
            AND NOT tblGesamt.geloescht
            AND NOT tblGesamt.enthalten_in_af = "ka"
    ORDER BY tblUserIDundName.name
    ;

    --
    -- Finde vorhandene AFen zu Rollen technischer User
    --
    DROP TABLE IF EXISTS patchTU_bekannteTUAFKombinationen;
    CREATE TABLE patchTU_bekannteTUAFKombinationen
    SELECT DISTINCT tblUserIDundName.name,
        tblUserIDundName.userid,
        tbl_Rollen.rollenname,
        tbl_RolleHatAF.af,
        tbl_AFListe.af_name
    FROM `tblUserIDundName`
    INNER JOIN tbl_Rollen
        ON LEFT(concat("Technischer User: ", tblUserIDundName.name), 90) = tbl_Rollen.rollenname
        INNER JOIN tbl_RolleHatAF
            ON tbl_Rollen.rollenname = tbl_RolleHatAF.rollenname
            LEFT JOIN tbl_AFListe
                ON tbl_RolleHatAF.af = tbl_AFListe.id
    ;

    --
    -- Finde die Unterschiede (Nur Anzeige zum Checken)
    --
    SELECT patchTU_alleAF.*,
        patchTU_bekannteTUAFKombinationen.*
    FROM `patchTU_alleAF`
    LEFT JOIN patchTU_bekannteTUAFKombinationen
        ON patchTU_alleAF.rollenname = patchTU_bekannteTUAFKombinationen.rollenname
            AND patchTU_alleAF.enthalten_in_af = patchTU_bekannteTUAFKombinationen.af_name
        INNER JOIN tbl_AFListe
            ON patchTU_alleAF.enthalten_in_af = tbl_AFListe.af_name
    WHERE patchTU_bekannteTUAFKombinationen.af_name is null
    ;


    --
    -- Und jetzt das schnelle Update
    --
    TRUNCATE Patch_tbl_RolleHatAF;
    INSERT INTO Patch_tbl_RolleHatAF
    SELECT
                0 AS rollenmappingid,
                1 AS mussfeld,
                concat("Generiertes Recht für ", patchTU_alleAF.name) AS bemerkung,
                patchTU_alleAF.af AS af,
                patchTU_alleAF.rollenname AS rollenname,
                4 AS einsatz
    FROM `patchTU_alleAF`
                LEFT JOIN patchTU_bekannteTUAFKombinationen
        ON patchTU_alleAF.rollenname = patchTU_bekannteTUAFKombinationen.rollenname
                AND patchTU_alleAF.enthalten_in_af = patchTU_bekannteTUAFKombinationen.af_name
                            INNER JOIN tbl_AFListe
                            ON patchTU_alleAF.enthalten_in_af = tbl_AFListe.af_name
    WHERE patchTU_bekannteTUAFKombinationen.af_name is null
    ;


    SELECT COUNT(*) as "Anzahl einzutragender Werte" FROM Patch_tbl_RolleHatAF
    UNION
    SELECT COUNT(*) as "Anzahl vorher" FROM tbl_RolleHatAF;

    INSERT INTO tbl_RolleHatAF
        SELECT
            0 AS rollenmappingid,
            Patch_tbl_RolleHatAF.mussfeld,
            Patch_tbl_RolleHatAF.bemerkung,
            Patch_tbl_RolleHatAF.af,
            Patch_tbl_RolleHatAF.rollenname,
            Patch_tbl_RolleHatAF.einsatz
        FROM `Patch_tbl_RolleHatAF`
    ON DUPLICATE KEY UPDATE tbl_RolleHatAF.bemerkung = concat("Doppeleintrag: ", tbl_RolleHatAF.bemerkung);

    SELECT * FROM `Patch_tbl_RolleHatAF`
    LEFT JOIN tbl_Rollen
        ON Patch_tbl_RolleHatAF.rollenname = tbl_Rollen.rollenname
    WHERE tbl_Rollen.rollenname is null;
    SELECT COUNT(*) as "Anzahl nachher" FROM tbl_RolleHatAF;

    DROP TABLE IF EXISTS patchTU_bekannteTUAFKombinationen;
    DROP TABLE IF EXISTS patchTU_alleAF;

    --
    -- Aktualisiere Spezialrollen für Technische User
    --   Rollen müssen bereits bestehen und mit AFen verknüpft sein
    --

    INSERT INTO tbl_UserHatRolle
        SELECT 0 as userundrollenid,
            "Schwerpunkt" AS schwerpunkt_vertretung,
            "Spezifische Rolle für Technischen User" AS `bemerkung`,
            now() AS `letzte_aenderung`,
            LEFT(concat("Technischer User: ", tblUserIDundName.name), 90) AS `rollenname`,
            tblUserIDundName.userID,
            null as id

            FROM `tblUserIDundName`
            LEFT JOIN tbl_Rollen
                ON concat("Technischer User: ", tblUserIDundName.name) = tbl_Rollen.rollenname

        WHERE
            tblUserIDundName.userid like "xv86%"
                AND tblUserIDundName.zi_organisation = "ai-xa"
                AND NOT tblUserIDundName.geloescht
                AND tbl_Rollen.rollenname is not null
        ORDER BY tblUserIDundName.name
    ON DUPLICATE KEY UPDATE tbl_UserHatRolle.`letzte_aenderung` = now()
    ;

    SELECT * FROM tbl_UserHatRolle ORDER BY userundrollenid DESC LIMIT 1000;

ROLLBACK;

-- Danach manuelle Zuordnung der fehlenden UserHatRolle - Verbindungen


-- -----------------------------------------------------
--
-- Aktualisiere Spezialrollen für Technische User
--   Rollen müssen bereits bestehen und mit AFen verknüpft sein
--
-- -----------------------------------------------------

BEGIN;
    INSERT INTO tbl_UserHatRolle
        SELECT 0 as userundrollenid,
            "Schwerpunkt" AS schwerpunkt_vertretung,
            "Spezifische Rolle für Technischen User" AS `bemerkung`,
            now() AS `letzte_aenderung`,
            LEFT(concat("Technischer User: ", tblUserIDundName.name), 90) AS `rollenname`,
            tblUserIDundName.userID,
            null as id

            FROM `tblUserIDundName`
            LEFT JOIN tbl_Rollen
                ON concat("Technischer User: ", tblUserIDundName.name) = tbl_Rollen.rollenname

        WHERE
            tblUserIDundName.userid like "xv86%"
                AND tblUserIDundName.zi_organisation = "ai-xa"
                AND NOT tblUserIDundName.geloescht
                AND tbl_Rollen.rollenname is not null
        ORDER BY tblUserIDundName.name
    ON DUPLICATE KEY UPDATE tbl_UserHatRolle.`letzte_aenderung` = now()
    ;

    SELECT * FROM tbl_UserHatRolle ORDER BY userundrollenid DESC LIMIT 100;

ROLLBACK;
