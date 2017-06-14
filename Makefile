site_name=dcsl
port=9090
output_dir=build
to_crawl=10
docker_name="demo-$(site_name)"

all: clean static start

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

crawl:
	python src/jahiap.py -o $(output_dir) crawl $(site_name)

crawl_many:
	python src/jahiap.py -o $(output_dir) crawl -n $(to_crawl) $(site_name)

unzip:
	python src/jahiap.py -o $(output_dir) unzip $(site_name)

parse:
	python src/jahiap.py -o $(output_dir) parse $(site_name)

dict:
	python src/jahiap.py -o $(output_dir) export -d $(site_name)

static:
	python src/jahiap.py -o $(output_dir) export -s $(site_name)

start:
	docker run -d \
		--name $(docker_name) \
		--restart=always \
		-p $(port):80 \
		-v $(PWD)/$(output_dir)/$(site_name)_html:/usr/share/nginx/html \
		nginx

stop:
	docker rm -f $(docker_name);

restart: stop start