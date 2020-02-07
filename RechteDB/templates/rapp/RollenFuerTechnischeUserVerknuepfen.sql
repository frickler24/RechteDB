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

    SELECT * FROM tbl_UserHatRolle ORDER BY userundrollenid DESC LIMIT 1000;

ROLLBACK;
