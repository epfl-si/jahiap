port=9090
name=demo-static


start:
	docker run --name $(name) -p $(port):80 -v /tmp/dcsl/html:/usr/share/nginx/html -d nginx

stop:
	docker rm -f $(name)

restart: stop start