site_name=dcsl
zip_file=exports/dcsl_export_2017-06-09-18-20.zip
port=9090
output_dir=build
to_crawl=682
docker_name="demo-$(site_name)"

all: clean generate start

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

crawl_one:
	python src/jahiap.py -o $(output_dir) crawl --site $(site_name)

crawl_many:
	python src/jahiap.py -o $(output_dir) crawl -n $(to_crawl)

unzip:
	python src/jahiap.py -o $(output_dir) unzip $(zip_file)

parse:
	python src/jahiap.py -o $(output_dir) parse $(site_name)

dict:
	python jahiap.py -o $(output_dir) export $(site_name) -d

static:
	python src/jahiap.py -o $(output_dir) export $(site_name) -s

generate:
	python src/jahiap.py -o $(output_dir) unzip $(zip_file)
	python src/jahiap.py -o $(output_dir) export $(site_name) -s

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