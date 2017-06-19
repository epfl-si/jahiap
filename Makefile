site_name=master
number=1
output_dir=build
docker_name="demo-$(site_name)"

all: clean static start

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

crawl:
	python src/jahiap.py -o $(output_dir) -n $(number) crawl $(site_name)

unzip:
	python src/jahiap.py -o $(output_dir) -n $(number) unzip $(site_name)

parse:
	python src/jahiap.py -o $(output_dir) -n $(number) parse $(site_name)

dict:
	python src/jahiap.py -o $(output_dir) -n $(number) export -d $(site_name)

static:
	python src/jahiap.py -o $(output_dir) -n $(number) export -s $(site_name)

wp:
	python src/jahiap.py -o $(output_dir) export -w $(site_name)

clean_wordpress:
	python src/jahiap.py -o $(output_dir) export -c $(site_name)

start:
	docker run -d \
		--name $(docker_name) \
		--restart=always \
		--net wp-net \
		--label "traefik.enable=true" \
		--label "traefik.backend=static-$(site_name)" \
		--label "traefik.frontend=static-$(site_name)" \
		--label "traefik.frontend.rule=Host:$(WP_ADMIN_URL);PathPrefix:/static/$(site_name)" \
		-v $(PWD)/$(output_dir)/$(site_name)/$(site_name)_html:/usr/share/nginx/html/static/$(site_name) \
		nginx

stop:
	docker stop $(docker_name)
	docker rm -f $(docker_name)

restart: stop start
