A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

pip install -r requirements/base.txt

## Usage

~~~
$ python jahiap.py -i <export_file> -o <output_dir>
$ docker run -p 8080:80 -v <output_dir>/html:/usr/share/nginx/html -d nginx

Then go to http://localhost:8080
~~~

