site_name=master
port=9090
number=1
output_dir=build
docker_name="demo-$(site_name)"

all: clean static start

clean:
	rm -rf $(output_dir)

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

start:
	docker run -d \
		--name $(docker_name) \
		--restart=always \
		-p $(port):80 \
		-v $(PWD)/$(output_dir)/$(site_name)/$(site_name)_html:/usr/share/nginx/html \
		nginx

stop:
	docker rm -f $(docker_name);

restart: stop start