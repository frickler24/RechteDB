# vim:set ft=Makefile ts=8:

it:     clean netzwerk mariadb phpmyadmin halb
con:    it rappprod
coni:   it image rappprod
all:	it image rapptest rappprod status

clean:
	-docker rm -f rapp
	-docker rm -f phpmyadmin
	-docker rm -f mariadb
	-docker rm -f hap
	-docker network rm mariaNetz

netzwerk:
	docker network create --subnet 172.42.0.0/16 mariaNetz

mariadb:
	docker run -d \
		--name mariadb \
		--network mariaNetz \
		--network-alias maria \
		--restart unless-stopped \
		-p 13306:3306 \
        -e TZ='Europe/Berlin' \
		-e MYSQL_ROOT_PASSWORD=geheim \
		-v /home/lutz/datadir:/var/lib/mysql \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/mariadbconf.d:/etc/mysql/conf.d \
		mariadb:10.2

phpmyadmin:
	docker run -d \
		-p 8080:80 \
		--name phpmyadmin \
		--network mariaNetz \
		--network-alias pma \
		--restart unless-stopped \
        -e TZ='Europe/Berlin' \
		-e PMA_HOST=maria \
		mypma

phpmyadmin_pma:
	docker run -d \
		-p 8088:80 \
		--name phpmyadmin \
		--network mariaNetz \
		--network-alias pma \
		--restart unless-stopped \
        -e TZ='Europe/Berlin' \
		-e PMA_HOST=maria \
		-e PMA_CONTROLUSER=pma \
		-e PMA_CONTROLPASS=0oWiPLfdhAcSqy9TnmhKcI222QQIO87BvvjiHX9r57\
		mypma

importfile:
	cd irgendwohin
	zcat RechteDB\ 20180825\ Letzter\ Export\ vor\ Neuimplementierung.sql.gz > import.sql
	vi import.sql
	change
	docker cp import.sql mariadb:/tmp

tarfile:
	( \
		cd /home/lutz/Projekte/RechteDB2MySQL/ \
			&& rm -f RechteDB/code_* \
			&& tar cf /tmp/code_file.tar.gz RechteDB \
			&& mv /tmp/code_file.tar.gz RechteDB/code_$(shell grep "^__version__" RechteDB/rapp/__init__.py | cut -d\' -f 2).tar.gz \
	)

codefile:
	( \
		cd /home/lutz/Projekte/RechteDB2MySQL/ \
			&& rm -f RechteDB/code_* \
			&& tar cf /tmp/code_file_s390x.tar.gz \
                RechteDB/code \
                RechteDB/Dockerfile \
                RechteDB/Dockerfile_full \
                RechteDB/.dockerignore \
                RechteDB/Makefile \
                RechteDB/RechteDB \
                RechteDB/requirements.txt \
                RechteDB/Testfabrik_clear.csv \
                RechteDB/Testfabrik_init.csv \
                RechteDB/Testfabrik_run.csv \
                RechteDB/.git/branches \
                RechteDB/.git/COMMIT_EDITMSG \
                RechteDB/.git/config \
                RechteDB/.git/description \
                RechteDB/.git/FETCH_HEAD \
                RechteDB/.git/HEAD \
                RechteDB/.git/hooks \
                RechteDB/.git/index \
                RechteDB/.git/info \
                RechteDB/.git/logs \
                RechteDB/.git/ORIG_HEAD \
                RechteDB/.git/packed-refs \
                RechteDB/.git/refs \
			&& mv /tmp/code_file_s390x.tar.gz RechteDB/code_s390x_$(shell grep "^__version__" RechteDB/rapp/__init__.py | cut -d\' -f 2).tar.gz \
	)

image:
	( \
		cd /home/lutz/Projekte/RechteDB2MySQL/RechteDB/ \
			&& docker build -t rapp . \
	)

exportableImage:	tarfile image
	( \
		cd /home/lutz/Projekte/RechteDB2MySQL/RechteDB/ \
			&& docker build -t rapp_full -f Dockerfile_full . \
	)

datafile:
	( \
		cd /home/lutz \
			&& sudo tar czf datadir_Mainfrix_$(shell date +"%Y%m%d").tar.gz datadir \
			&& sudo chown lutz:lutz datadir_Mainfrix_$(shell date +"%Y%m%d") \
	)


export:	exportableImage
	docker save rapp_full | gzip -9 > /tmp/rapp_$(shell grep "^__version__" RechteDB/rapp/__init__.py | cut -d\' -f 2).tar.gz

rapptest:
	docker run -it --rm \
		--name testDjango \
		--network mariaNetz \
        -e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		rapp:latest sh -c "echo yes | /RechteDB/code/manage.py test -v2"

rappprod:
	docker run -d \
		--name rapp \
		-p 8089:8089 \
		--network mariaNetz \
		--network-alias rapp \
		--restart unless-stopped \
        -e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		rapp:latest

rappfull:
	-docker rm -f rapp
	docker run -d \
		--name rapp \
		-p 8089:8000 \
		--network mariaNetz \
		--network-alias rapp \
		--restart unless-stopped \
        -e TZ='Europe/Berlin' \
		rapp_full:latest

status:
	sleep 1
	docker ps

halb:
	-docker run -d \
		--restart unless-stopped \
		--name hap \
		--publish 8088:80 \
		--network mariaNetz \
		--network-alias hap \
		-e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cnf \
		haproxy haproxy -f /usr/local/etc/haproxy/haproxy.cnf -d -V


