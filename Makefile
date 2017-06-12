site_name=master
zip_file=exports/dcsl_export_2017-06-07-08-08.zip
port=9090
output_dir=build
docker_name="demo-$(site_name)"

all: clean generate start

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

generate:
	python jahiap.py -o $(output_dir) unzip $(zip_file)
	python jahiap.py -o $(output_dir) export $(site_name) -s

start:
	docker run -d \
		--name $(docker_name) \
		-p $(port):80 \
		-v $(PWD)/$(output_dir)/$(site_name)_html:/usr/share/nginx/html \
		nginx

stop:
	docker rm -f $(docker_name);

restart: stop start