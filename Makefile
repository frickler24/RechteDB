# vim:set ft=Makefile ts=8:

it:	 clean netzwerk mariadb phpmyadmin hap
con:	it rappprod
coni:   it image rappprod
all:	it image codefile rapptest rappprod status

clean:
	-docker rm -f rapp
	-docker rm -f pma
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

crawler:
	docker run -it --rm \
		--name crawlewr \
		--network mariaNetz \
		-v /home/lutz/schemadir:/home/schcrwlr/share \
		--network-alias crawler \
		-e TZ='Europe/Berlin' \
		--entrypoint=/bin/bash \
		schemacrawler/schemacrawler

phpmyadmin:
	docker run -d \
		--name pma \
        --publish 8888:80 \
		--network mariaNetz \
		--network-alias pma \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-e PMA_HOST=maria \
		mypma

WEGDAMITpma:
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
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/.env.docker:/RechteDB/.env \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB/.env.docker:/RechteDB/code/.env \
		rapp:latest sh -c "/RechteDB/code/manage.py test --no-input"

rapptest2:
	docker run -it --rm \
		--name testDjango \
		--network mariaNetz \
		-e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		rapp:latest bash

rappprod:
	docker run -d \
		--name rapp \
		--network mariaNetz \
		--network-alias rapp \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/.env.docker:/RechteDB/.env \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB/.env.docker:/RechteDB/code/.env \
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

vieleweg:
	@echo $(shell bash -c 'for i in {1..10}; do docker rm -f rapp$$i; done')

rappviele: vieleweg
	@echo $(shell bash -c 'for i in {1..10}; do \
		docker run -d \
			--name rapp$$i \
			--network mariaNetz \
			--network-alias rapp$$i \
			--restart unless-stopped \
			-e TZ='Europe/Berlin' \
			-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB:/RechteDB \
			-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/RechteDB:/RechteDB/code \
			rapp:latest; done')

chaos:
	docker login -u=_ -p=$$CMKEY docker.steadybit.io
	docker pull docker.steadybit.io/steadybit/agent
	docker run \
		--detach \
        --restart always \
		--name steadybit-agent \
		--volume /var/run:/var/run \
		--privileged \
		--net=host \
		--pid=host \
		--ipc=host \
		--restart unless-stopped \
		--env="STEADYBIT_AGENT_KEY=$$CMKEY" \
		--env="STEADYBIT_AGENT_REGISTER_URL=https://platform.chaosmesh.io" \
		docker.steadybit.io/steadybit/agent

nochaos:
	-docker container rm -f steadybit-agent

prod:
	(cd RechteDB; docker-compose up -d)

prodoff:
	(cd RechteDB; docker-compose down -t 1)

prodneu:
	(cd RechteDB && docker-compose build --no-cache && docker-compose up --detach --force-recreate)

vorbereitung:
	-docker rm -f hap
	make hap_port80und443
	@echo "Ports 80 und 443 freischalten im Router für den Docker-Host, dann <Return>"
	@read a

letsencrypt: vorbereitung
	docker run -it \
		--rm \
		--name certcont \
		--ip=172.42.0.99 \
		--network mariaNetz \
		--network-alias letsencrypt \
		--volume "/home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/letsencrypt/etc:/etc/letsencrypt:rw" \
		--volume "/home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/letsencrypt/var:/var/lib/letsencrypt:rw" \
		certbot/certbot:latest \
			certonly --standalone \
				-d frickler.eichler-web.de \
				--non-interactive \
				--preferred-challenges http \
				--agree-tos \
				--email m5@frickler24.de \
				--http-01-port=80
				sudo chown lutz /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/letsencrypt/etc/live/frickler.eichler-web.de/privkey.pem
		cat /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/letsencrypt/etc/live/frickler.eichler-web.de/fullchain.pem \
			/home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/letsencrypt/etc/live/frickler.eichler-web.de/privkey.pem \
			> /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/certs/RApp.pem
		docker rm -f hap
		make hap
		@echo
		@echo "Nun die Ports 80 und 443 wieder auf den ursprünglichen Stand zurücksetzen".

hap:
	-docker run -d \
		--name hap \
		--publish 8088:80 \
		--publish 18443:443 \
		--network mariaNetz \
		--network-alias hap \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/haproxy:/usr/local/etc/haproxy:ro \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/certs:/certs:ro \
		haproxy haproxy -f /usr/local/etc/haproxy/haproxy.cnf -d -V


hap_port80und443:
	-docker run -d \
		--name hap \
		--restart unless-stopped \
		--publish 80:80 \
		--publish 443:443 \
		--publish 8088:80 \
		--publish 18443:443 \
		--network mariaNetz \
		--network-alias hap \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/haproxy:/usr/local/etc/haproxy:ro \
		-v /home/lutz/Projekte/RechteDB2MySQL/RechteDB/other_files/certs:/certs:ro \
		haproxy haproxy -f /usr/local/etc/haproxy/haproxy.cnf -d -V


