# RechteDB
<b>Development for database and UI for managing AIM.

It is for internal use only, therefor documentation is done in german language.</b>

# Vorbereitung Image
Für den Fall, dass ein völlig neuer Server aufgesetzt werden muss und kein akueller Server existiert,
müssen die erforderlichen INformationen über den Client auf den Server geladen werden.
- Login auf dem Server mit Putty
- Öffnen eines lokalen CMD-Fensters
```
c:
cd \users\USER\Downloads
psftp PROFILNAME (macht Login mit denselben credentials wie sie die offene Verbindung hat)

cd tarfiles (das geschieht remote)
put bashfiles.tar.gz
put config_x86.tar.gz
put datadir_<DATUM>.tar.gz
put rapp_<VERSION>.tar.gz
```
  Geduld{,,,,,}

- Wenn man will, im Online-Fenster draufgucken mit
`watch -n 10 ls -lt ~/tarfiles/rapp* | tail -1`

- Das kann man mit STRG-C abbrechen.

Irgendwann ist der Upload fertig. 
Nun muss das hochgeladene Image-Tar in docker geladen werden:
```
make neu
```
Damit werden sowohl ein rapp:latest als auch das entsprechende Tag oben angelegt.
ZUsätzlich wurde das Image als latest und mit der aktuellen Versionsnummer im Harbor abgelegt.
Dafür macht make ein docker login auf den Harbor
```
docker image ls
```
# Umkopieren der vorhandenen Daten
- `make sicherung` im Home-Verzeichnis erzeugt auf dem aktuellen Server in ~/tarfiles/ sowohl ein Backup der Daten, 
als auch die Menge der Konfigurationsdateien, jeweils als gezipptes Tarfile.
- ToDo: das ist hier noch inkonsistent
- Dann erfolgt das Zurückspielen der maschinenspezifischen Elemente:
```
Hochladen des Schlüsselpaares vom Client auf die Zielmaschine,
Akzeptieren des öffentlichen Schlüssels auf der Zielmaschine
cp -r ~/tarfiles ZIELMASCHINE:.
```
- Entpacken der bash-Dateien, des Datenverzeichnisses und der Konfigurationsdateien
- Anpassen der Konfigdatei für Django (erlaubte Server-Zugriffe)

# Generieren der Container
- Das komplette Neuaufsetzen der drei Container + Netzwerk kann beliebig häufig wiederholt werden. 
Insbesondere nach Systemneustarts kann damit die gesamt Anwendung erneut hochgefahren werden.

Das sollte mal auf docker-compose umgestellt werden, dazu ist das ja mal erfunden worden.
Allerdings müssen dann die Nutzung des manage.py test und das Test-curl (s.u.) anders aufgebaut werden.

`make`

- Abschließend wird im make zum Test ein curl auf den erzeugten Weberserver durchgeführt 
und nach einer bestimmten Zeile der Einstiegsseite gesucht.

Die Ausgabe (mit aktueller Berechtigungszahl) sollte folgendermaßen aussehen:

`        <div class="col col-xs-2 col-sm-2 col-md-2 col-lg-2 col-xl-2 text-right bg-info">38604</div>`

# Nutzung via Browser
Genutzt werden kann die App in vernünftigen Browsern (nicht IE11, der weiß nicht, wie breit seine Fenster sind)
über die URL http://\<HOSTNAME wie in putty\>

# ToDos
Wichtige noch fehlende Aktivitäten oder gute Ideen werden 
- bei Fehlern als Issue im github vermerkt
- Notwendige Erweiterungen sollen ebenfalls im Projekt auf Github gesammelt werden, weil damit die Priorisierung einfacher wird.
- bei Kleinigkeiten im jeweiligen Programm angelegt (Suche über die jeweilige SEU nach "ToDo:")
