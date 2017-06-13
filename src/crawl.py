"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
"""
    This script automates the crawling of Jahia website,
    in order to download zip exports.

    Run
        `python crawl.py -h`
    to get help on usage and available options
"""

import logging
import os
import timeit
from datetime import datetime, timedelta
from pathlib import Path

import requests
from clint.textui import progress

from settings import JAHIA_SITES

# define HOST
if not os.environ.get("JAHIA_HOST"):
    logging.warning("JAHIA_HOST not set, using 'localhost' as default")
HOST = os.environ.get("JAHIA_HOST", "localhost")

# define credentials
if not os.environ.get("JAHIA_ROOT_PASSWORD"):
    raise SystemExit("The script requires the environment variable JAHIA_ROOT_PASSWORD to be set")
if not os.environ.get("JAHIA_ROOT_USER"):
    logging.warning("JAHIA_ROOT_USER not set, using 'root' as default")

ID_POST_PARAMS = {
    'login_username': os.environ.get('JAHIA_ROOT_USER', 'root'),
    'login_password': os.environ.get('JAHIA_ROOT_PASSWORD')
}

# define URLs and their parameters
ID_URI = "administration"
ID_GET_PARAMS = {
    'do': 'processlogin',
    'redirectTo': '/administration?null'
}
DWLD_URI = "site/2dmaterials2016/op/edit/page-131253.html/engineName/export"
DWLD_GET_PARAMS = {
    'do': 'sites',
    'sub': 'multipledelete',
    'exportformat': 'site'
}


class SiteCrawler(object):
    """
        Call SiteCrawler(cmd_args).download()

        'cmd_args' drives the download logic, i.e:
        * '--site': what unic site to download
        * '-n' & '-s': or how many sites to download from JAHIA_SITES, where from
        * '--date': what date should be asked Jahia
        * '--force': if existing downloaded files should be overrident or not
     """

    FILE_PATTERN = "%s_export_%s.zip"
    TRACER = "tracer_crawling.csv"

    # singleton, with lazy initialization
    __session = None

    @property
    def session(self):
        """
            Make a POST on Jahia administration to get a valid session
        """
        if self.__session is None:
            # lazy initialization
            logging.info("authenticating...")
            session = requests.Session()
            response = session.post(
                "%s/%s" % (HOST, ID_URI),
                params=ID_GET_PARAMS,
                data=ID_POST_PARAMS
            )

            # log and set session
            logging.info("requested %s", response.url)
            logging.debug("returned %s", response.status_code)
            self.__session = session

        # cls.session is set, return it
        return self.__session

    @classmethod
    def download(cls, cmd_args):
        """
            Download either the one site 'cmd_args.site'
            or all 'cmd_args.number' sites from JAHIA_SITES, starting at 'cmd_args.start_at'
        """
        if cmd_args.site:
            # download only given self.site
            cls(cmd_args.site, cmd_args).download_site()
        else:
            # download sites from JAHIA_SITES
            start = int(cmd_args.start_at)
            end = int(cmd_args.start_at) + int(cmd_args.number)
            sites = JAHIA_SITES[start:end]
            for site in sites:
                cls(site, cmd_args).download_site()

    def __init__(self, site_name, cmd_args):
        self.site_name = site_name
        self.date = cmd_args.date
        self.output = cmd_args.output
        self.force = cmd_args.force
        self.elapsed = 0

        # adapt file_path to cmd_args
        existing = self.already_downloaded()
        if existing and not self.force:
            self.file_path = existing[-1]
            self.file_name = os.path.basename(self.file_path)
        else:
            self.file_name = self.FILE_PATTERN % (self.site_name, self.date)
            self.file_path = os.path.join(self.output, self.file_name)

    def __str__(self):
        """ Format used for report"""
        return ";".join([self.site_name, self.file_path, str(self.elapsed)])

    def already_downloaded(self):
        path = Path(self.output)
        return list(path.glob("%s_export*" % self.site_name))

    def download_site(self):
        # do not download twice if not --force
        existing = self.already_downloaded()
        if existing and not self.force:
            logging.warning("%s already downloaded %sx. Last one is %s",
                self.site_name, len(existing), self.file_path)
            return self.file_path

        # pepare query
        params = DWLD_GET_PARAMS.copy()
        params['sitebox'] = self.site_name

        # set timer to measure execution time
        start_time = timeit.default_timer()

        # make query
        logging.debug("downloading %s...", self.file_name)
        response = self.session.post(
            "%s/%s/%s" % (HOST, DWLD_URI, self.file_name),
            params=params,
            stream=True
        )
        logging.debug("requested %s", response.url)
        logging.debug("returned %s", response.status_code)

        # raise exception in case of error
        if not response.status_code == requests.codes.ok:
            response.raise_for_status()

        # adapt streaming function to content-length in header
        logging.debug("headers %s", response.headers)
        total_length = response.headers.get('content-length')
        if total_length is not None:
            def read_stream():
                return progress.bar(
                    response.iter_content(chunk_size=4096),
                    expected_size=(int(total_length)/4096) + 1)
        else:
            def read_stream():
                return response.iter_content(chunk_size=4096)

        # download file
        logging.info("saving response into %s...", self.file_path)
        with open(self.file_path, 'wb') as output:
            for chunk in read_stream():
                if chunk:
                    output.write(chunk)
                    output.flush()

        # log execution time and return path to downloaded file
        self.elapsed = timedelta(seconds=timeit.default_timer() - start_time)
        logging.info("file downloaded in %s", self.elapsed)
        tracer_path = os.path.join(self.output, self.TRACER)
        with open(tracer_path, 'a') as tracer:
            tracer.write(str(self))
            tracer.flush()
        return self.file_path


import argparse


def main(args):
    logging.info("starting crawling...")
    logging.debug("HOST set to %s", HOST)
    logging.debug("DATE set to %s", args.date)
    try:
        SiteCrawler.download(args)
    except requests.ConnectionError as err:
        logging.error(err)


if __name__ == '__main__':
    # declare parsers for command line arguments
    parser = argparse.ArgumentParser(
        description="Crawl 'NUMBER' Jahia zip files from JAHIA_SITES, starting at 'START_AT' index. Or crawl given  'SITE'")

    # logging-related agruments
    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        help='Set logging level to DEBUG (default is INFO)')
    parser.add_argument('--quiet',
                        dest='quiet',
                        action='store_true',
                        help='Set logging level to WARNING (default is INFO)')

    # Jahia related arguments
    parser.add_argument('--site',
                        action='store',
                        help='site name (in jahia admin) of site to get the zip for')
    parser.add_argument('-o', '--output',
                        action='store',
                        default='build',
                        help='path where to download files')
    parser.add_argument('-f', '--force',
                        dest='force',
                        action='store_true',
                        help='Force download even if exisiting files for same site')
    parser.add_argument('-d', '--date',
                        action='store',
                        default=datetime.today().strftime("%Y-%m-%d-%H-%M"),
                        help='date and time for the snapshot, e.g : 2017-01-15-23-00')
    parser.add_argument('-n', '--number',
                        action='store',
                        type=int,
                        default=1,
                        help='number of sites to crawl in JAHIA_SITES')
    parser.add_argument('-s', '--start-at',
                        action='store',
                        dest='start_at',
                        type=int,
                        default=0,
                        help='(zero-)index where to start in JAHIA_SITES')

    args = parser.parse_args()

    # set logging config before anything else
    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # check output
    if not os.path.isdir(args.output):
        raise SystemExit("Ouput '%s' does not exist. Please create it first" % args.output)

    main(args)
