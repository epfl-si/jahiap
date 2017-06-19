site_name=master
number=1
output_dir=build

all: clean static start

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
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --to-wordpress

clean_wordpress:
	python src/jahiap.py export $(site_name) --output-dir $(output_dir) --clean-wordpress

run:
	python src/jahiap.py docker $(site_name) --output-dir $(output_dir) --number $(number)
