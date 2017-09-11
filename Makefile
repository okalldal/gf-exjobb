IMG_NAME = exjobb

build:
	docker build -t $(IMG_NAME) .

notebook:
	docker run -d -p 8888:8888 \
	-v $(PWD)/work:/home/jovyan/work \
	-v $(PWD)/data:/home/jovyan/data \
	$(IMG_NAME)
	sleep 2
	make logs

logs:
	docker logs `docker ps -q`

stop:
	docker stop `docker ps -q`; docker rm `docker ps -aq`

console:
	docker run -it --rm -w /home/jovyan/work \
	-v $(PWD)/work:/home/jovyan/work \
	-v $(PWD)/data:/home/jovyan/data \
	$(IMG_NAME) bash

data:
	mkdir -p data && cd data && \
	curl -SL http://trainomatic.org/data/train-o-matic-data.zip | tar xz && \
	curl -SL https://github.com/UniversalDependencies/UD_English/archive/r1.3.tar.gz | tar xz