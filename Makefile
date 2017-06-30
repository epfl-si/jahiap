site_name=dcsl
number=1
output_dir=build
docker_name="demo-$(site_name)"
port=9090

all: clean run

clean:
	rm -rf $(output_dir)/$(site_name)*
	rm -rf $(output_dir)/parsed_$(site_name).pkl

crawl:
	python src/jahiap.py crawl $(site_name) --output-dir $(output_dir) --number $(number)

unzip:
	python src/jahiap.py unzip $(site_name) --output-dir $(output_dir) --number $(number)

parse:
	python src/jahiap.py parse $(site_name) --output-dir $(output_dir) --number $(number)

dict:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --number $(number) --to-dictionary

static:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --number $(number) --to-static

wp:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --to-wordpress --site-url $(WP_ADMIN_URL) --wp-cli "wpcli"

wp_all:
	screen -RD wpimport
	python src/jahiap.py export $(site_name) -w --wp-cli=wp-cli-wp-import --number=$(number) --output-dir=/mnt/export/build --use-cache --debug >> /home/team/import-wp.log

nginx_conf:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --nginx-conf --site-url $(WP_ADMIN_URL) --wp-cli "wpcli"

clean_wordpress:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --clean-wordpress --site-url $(WP_ADMIN_URL) --wp-cli "wpcli"

run:
	python src/jahiap.py docker $(site_name) --output-dir $(output_dir) --number $(number)

standalone:
	docker run -d \
		--name $(docker_name) \
		-p $(port):80 \
		-v $(PWD)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
		-v $(PWD)/$(output_dir)/$(site_name)/html:/usr/share/nginx/html \
		nginx

stop_standalone:
	docker stop $(docker_name)
	docker rm $(docker_name)

generate:
	python src/jahiap.py generate

