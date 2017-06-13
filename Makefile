site_name=master
zip_file=exports/master_export_2017-05-29-10-53.zip
port=9090
output_dir=build
docker_name="demo-$(site_name)"

all: clean generate start

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

unzip:
	python src/jahiap.py -o $(output_dir) unzip $(zip_file)

parse:
	python src/jahiap.py -o $(output_dir) parse $(site_name)

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