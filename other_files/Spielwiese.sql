
-- Zählen der Einträge in der Gesamttabelle
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


-- Ein-Ausschalten des SQL-Loggings inkl. Auswertungen 
SET global general_log = 1;
SET global log_output = 'table';
SET global general_log = 0;

SELECT * FROM `mysql`.`general_log` WHERE event_time  > (now() - INTERVAL 8 SECOND) AND `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC
SELECT * FROM `mysql`.`general_log` WHERE `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC




-- Löschen von Einträgen in der RechteDB, bei denen die User bereits belöscht wurden (ca. 900 Stück)

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





(echo "use RechteDB;"; cat RechteDB_table_*) | mysql -uroot -pgeheim


-- Suche nach doppelten Einträgen in der UserUndIhreRollen-Tabelle
SELECT tbl_UserHatRolle.`UserID`, 
	tbl_UserHatRolle.`RollenName`, 
	tbl_UserHatRolle.`UserUndRollenID`, tbl_UserHatRolle.`Schwerpunkt/Vertretung`, 
	tbl_UserHatRolle.`Bemerkung`, tbl_UserHatRolle.`Letzte Änderung`

FROM tbl_UserHatRolle
WHERE (((tbl_UserHatRolle.`UserID`) 
	In (SELECT `UserID` 
	FROM `tbl_UserHatRolle` As Tmp 
	GROUP BY `UserID`,`RollenName` 
	HAVING Count(*)>1  
		And `RollenName` = `tbl_UserHatRolle`.`RollenName`)))
ORDER BY tbl_UserHatRolle.`UserID`, tbl_UserHatRolle.`RollenName`;
