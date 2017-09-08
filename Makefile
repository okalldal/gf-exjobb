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