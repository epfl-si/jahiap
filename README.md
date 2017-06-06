A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

pip install -r requirements/base.txt

## Usage

When developing

~~~
$ python jahiap.py -i <export_file> -o <output_dir> -d localhost
$ docker run -p 8080:80 -v <output_dir>/html:/usr/share/nginx/html -d nginx

Then go to http://localhost:8080 for static files
and to http://localhost for WordPress
~~~

If you only want to push to test-web-wordpress.epfl.ch, you can omit the last two options in the python script :

~~~
$ python jahiap.py -i <export_file>

Then go to http://test-web-wordpress.epfl.ch
~~~


## Testing

The testing tool [pytest](https://docs.pytest.org/en/latest/contents.html) comes with the requirements. You can run the full suite with :

```
$ pytest
...
```

Or you might choose to target some of those specific areas:

* TestSiteProperties
* TestSiteStructure
* TestSidebar
* TestHomepage


```
$ pytest -k TestSiteStructure
...
```
