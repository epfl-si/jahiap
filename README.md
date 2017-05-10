A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

pip install -r requirements/base.txt

## Run

~~~
python jahiap.py
docker run -p 8080:80 -v /tmp/jahiap:/usr/share/nginx/html -d nginx
Then go to http://localhost:8080
~~~

