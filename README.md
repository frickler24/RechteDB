# RechteDB
<b>Development for database and UI for managing AIM.

It is for internal use only, therefor documentation is done in german language.</b>

# Usage:
- Login auf dem Server mit Putty RechteDB-x86

- Öffnen eines lokalen CMD-Fensters
```
c:
cd \users\xv13254\Downloads
psftp RechteDB-x86 (macht Login mit denselben credentials wie sie die offene Verbindung hat)

cd tarfiles (das geschieht remote)
put rapp_<VERSION>.tar.gz
```

  Geduld{,,,,,}

- Wenn man will, im Online-Fenster draufgucken mit

`watch -n 10 ls -l ~/tarfiles/rapp*`

- Das kann man mit STRG-C abbrechen
Irgendwann ist der Upload fertig.

Nun muss das hochgeladene Image-Tar in docker geladen werden:
```
zcat ~/tarfiles/rapp_<VERSION>.tar.gz | docker image load
docker image tag rapp:latest f4s-docker.ruv.de/rechtedb/rapp:<VERSION>
```
Damit sollten sowohl ein rapp:latest als auch das entsprechende Tag oben angelegt worden sein.
```
docker image ls
docker login
docker push f4s-docker.ruv.de/rechtedb/rapp:<VERSION>
```
- Leider kann man den aktuellen Stand auf den Servern nur ohne den git-Verlauf laden (über zip-File). Erst mit dem Cloning eines eigenen Repos und Netzzugriff ginge das auch direkt.
So muss das Repo irgendwo auf einem git-fähigen Entwicklungsrechner ge-clone-t  und das Ergebnis komplett wieder über psftp kopiert werden 

`put RechteDB.git.tar.gz`

und im Online-Window:
`cd ; tar xvfz tarfiles/Rechtedb.git.tar.gz`

- Dann erfolgt das Zurückspielen der maschinenspezifischen Elemente:
```
cp RechteDB/RechteDB/.env.x86  RechteDB/RechteDB/.env
cp RechteDB/mariadbconf.d/my.cnf.x86 RechteDB/mariadbconf.d/my.cnf
cp RechteDB/Makefile.x86 RechteDB/Makefile
```
- Jetzt noch das komplette Neuaufsetzen der drei Container + Netzwerk

`make`

- Abschließend wird im make noch ein curl auf den erzeugten Weberserver durchgeführt 
und nach einer bestimmten Zeile der Einstiegsseite gesucht.

Die Ausgabe (mit aktueller Berechtigungszahl) sollte folgendermaßen aussehen:

`        <div class="col col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right bg-info">38604</div>`

Genutzt werden kann die App in vernünftigen Browsern (nicht IE11, der weiß nicht, wie breit seine Fenster sind)
über die URL http://\<HOSTNAME wie in putty\>

