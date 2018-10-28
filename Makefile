# vim:set ft=Makefile ts=8:

it:	clean netzwerk mariadb phpmyadmin 

all:	it image rapptest rappprod status

clean:
	-docker rm -f rapp
	-docker rm -f phpmyadmin
	-docker rm -f mariadb
	-docker network rm mariaNetz

netzwerk:
	docker network create --subnet 172.42.0.0/16 mariaNetz

mariadb:
	docker run -d \
		--name mariadb \
		--network mariaNetz \
		--network-alias maria \
		-p 13306:3306 \
		-e MYSQL_ROOT_PASSWORD=geheim \
		-v /home/lutz/datadir:/var/lib/mysql \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/mariadbconf.d:/etc/mysql/conf.d \
		mariadb:10.2


phpmyadmin:
	docker run -d \
		-p 8080:80 \
		--name phpmyadmin \
		--network mariaNetz \
		-e PMA_HOST=maria \
		phpmyadmin/phpmyadmin

phpmyadmin_pma:
	docker run -d \
		-p 8088:80 \
		--name phpmyadmin \
		--network mariaNetz \
		-e PMA_HOST=maria \
		-e PMA_CONTROLUSER=pma \
		-e PMA_CONTROLPASS=0oWiPLfdhAcSqy9TnmhKcI222QQIO87BvvjiHX9r57\
		phpmyadmin/phpmyadmin

importfile:
	cd irgendwohin
	zcat RechteDB\ 20180825\ Letzter\ Export\ vor\ Neuimplementierung.sql.gz > import.sql
	vi import.sql
	change
	docker cp import.sql mariadb:/tmp

image:	
	( \
		cd /home/lutz/Projekte/RechteDB2MySQL/RechteDB/ \
		&& docker build -t rapp . \
	)

exportableImage:	image
	docker save rapp | gzip -9 > /tmp/rapp_0.0.2.tar.gz

rapptest:
	docker run -it --rm \
		--name testDjango \
		--network mariaNetz \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		rapp:latest /RechteDB/code/manage.py test -v2

rappprod:
	docker run -d \
		--name rapp \
		-p 8089:8000 \
		--network mariaNetz \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		rapp:latest

status:
	sleep 1
	docker ps

