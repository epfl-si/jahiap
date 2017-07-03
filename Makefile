site_name=dcsl
number=1
output_dir=build
docker_name="demo-$(site_name)"
port=9090

# used for command wp_all: specify to which WP import data
wp_cli_import=wp-cli-wp-import
wp_host_import=wordpress.localhost
wp_path_import=admin/wp-import
output_dir_import=build
logs_import=build/import-wp.log

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
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --to-wordpress --site-host $(WP_ADMIN_HOST) --site-path $(WP_ADMIN_PATH) --wp-cli "wpcli"

wp_all:
	python src/jahiap.py export $(site_name) -w --site-host $(wp_host_import) --site-path $(wp_path_import) --wp-cli=$(wp_cli_import) --number=$(number) --output-dir=$(output_dir_import) --use-cache --debug >> $(logs_import)

nginx_conf:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --nginx-conf --site-host $(WP_ADMIN_HOST) --site-path $(WP_ADMIN_PATH) --wp-cli "wpcli"

clean_wordpress:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --clean-wordpress --site-host $(WP_ADMIN_HOST) --site-path $(WP_ADMIN_PATH) --wp-cli "wpcli"

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

