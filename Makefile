build:
	docker build -t exjobb .

notebook:
	docker run -d -p 8888:8888 -v $(PWD)/work:/home/jovyan/work exjobb
	sleep 2
	docker logs `docker ps -q`

stop:
	docker stop `docker ps -q`; docker rm `docker ps -aq`

console:
	docker run -it --rm -v $(PWD)/work:/home/jovyan/work -w /home/jovyan/work exjobb bash

data:
	mkdir -p data && cd data && \
	curl -SL http://trainomatic.org/data/train-o-matic-data.zip | tar xz && \
	curl -SL https://github.com/UniversalDependencies/UD_English/archive/r1.3.tar.gz | tar xz