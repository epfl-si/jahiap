A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

If you wish to work on one of the following features : *sites on same.domain/different/paths*, *wordpress*,  *redirections and proxy*, you need to setup your environment as described in `template-web-wordpress/`[README](https://github.com/epfl-idevelop/template-web-wordpress/blob/master/README.md)

If you only want to crawl, unzip, parse, generate static HTML and serve it in a standalone container, you should only need:

```
pip install -r requirements/base.txt
```

And the following environment variables (in order to crawl the zip files from Jahia):

```
export JAHIA_HOST="localhost"
export JAHIA_ROOT_USER='root'
export JAHIA_ROOT_PASSWORD=xxx
```

`JAHIA_ROOT_PASSWORD` is mandatory, i.e the script will not run if it is not set. For the two first ones, the values above are used by default.

## The 30-seconds tutorial (standalone, working on master.epfl.ch)

```
$ cd jahiap
$ make static standalone
```

You now can access the content at [http://localhost:9090](http://localhost:9090). If you want to stop the running container, you can use `make stop_standalone`.

For another website, e.g dcsl :

```
$ make static standalone port=9091 site_name=dcsl
```

This one will be available at [http://localhost:9091](http://localhost:9091).


## The 2-mins-seconds tutorial (with the whole architecture, on master.epfl.ch)

You first have to setup the environment as described in `template-web-wordpress/`[README](https://github.com/epfl-idevelop/template-web-wordpress/blob/master/README.md)

When you have your environment ready, you can start the helpers:

```
$ cd ~/git-repos/template-web-wordpress/helpers
$ make restart
...
```

You can check your DB on [phpmyadmin.localhost:8081](http://phpmyadmin.localhost:8081) and check that traefik is running on [http://localhost:8080](http://localhost:8080)

```
$ cd ~/git-repos/jahiap
$ make all
```

The website is now accessible on $WP_HOST/$WP_PATH/site_name. With the default values from the setup instructions, it will be available at [http://static.localhost/labs/master](http://static.localhost/labs/master).


For another website, e.g dcsl, you need to set the site_name

```
$ cd jahiap
$ make all site_name=dcsl
```

With the default values from the setup instructions, it will be available at [http://static.localhost/labs/dcsl](http://static.localhost/labs/dcsl).


## More details on usage

The `make` only wraps the calls to the script `src/jahiap.py`
