"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import logging
import os
from timeit import default_timer as timer
from collections import OrderedDict
from pathlib import Path

import requests
from clint.textui import progress

from settings import JAHIA_SITES
from utils import Utils

"""
    This script automates the crawling of Jahia website,
    in order to download zip exports.

    Run
        `python crawl.py -h`
    to get help on usage and available options
"""


class SiteCrawler(object):
    """
        Call SiteCrawler.download(cmd_args)

        'cmd_args' drives the download logic, i.e:
        * '--site': what unic site to download
        * '-n' & '-s': or how many sites to download from JAHIA_SITES, where from
        * '--date': what date should be asked to Jahia
        * '--force': if existing downloaded files should be overriden or not
     """

    # define HOST
    HOST = Utils.get_optional_env("JAHIA_HOST", "localhost")

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
                "%s/%s" % (self.HOST, self.ID_URI),
                params=self.ID_GET_PARAMS,
                data=self.get_credentials()
            )

            # log and set session
            logging.info("requested %s", response.url)
            logging.debug("returned %s", response.status_code)
            self.__session = session

        # cls.session is set, return it
        return self.__session

    @staticmethod
    def get_credentials():
        # define credentials
        return {
            'login_username': Utils.get_optional_env('JAHIA_ROOT_USER', 'root'),
            'login_password': Utils.get_required_env('JAHIA_ROOT_PASSWORD')
        }

    @classmethod
    def download(cls, cmd_args):
        """
            Download either the one site 'cmd_args.site_name'
            or all 'cmd_args.number' sites from JAHIA_SITES, starting at 'cmd_args.start_at'

            returns list of downloaded_files
        """
        logging.debug("HOST set to %s", cls.HOST)
        logging.debug("DATE set to %s", cmd_args['--date'])

        # to store paths of downloaded zips
        downloaded_files = OrderedDict()

        # compute list fo sites to download
        try:
            start_at = JAHIA_SITES.index(cmd_args['<site>'])
        except ValueError:
            raise SystemExit("site name %s not found in JAHIA_SITES", cmd_args['<site>'])
        end = start_at + int(cmd_args['--number'])
        sites = JAHIA_SITES[start_at:end]

        # download sites from JAHIA_SITES
        for site in sites:
            try:
                downloaded_files[site] = str(cls(site, cmd_args).download_site())
            except Exception as err:
                logging.error("%s - crawl - Could not crawl Jahia - Exception: %s", site, err)

        # return results, as strings
        return downloaded_files

    def __init__(self, site_name, cmd_args):
        self.site_name = site_name
        # jahia download URI depends on date
        self.date = cmd_args['--date']
        # where to store zip files
        self.export_path = cmd_args['--export-path']
        # where to store output from the script (tracer)
        self.output_path = cmd_args['--output-dir']
        # whether overriding existing zip or not
        self.force = cmd_args['--force-crawl']
        # to measure overall download time for given site
        self.elapsed_time = 0

        # adapt file_path to cmd_args
        existing = self.already_downloaded()
        if existing and not self.force:
            self.file_path = existing[-1]
            self.file_name = os.path.basename(self.file_path)
        else:
            self.file_name = self.FILE_PATTERN % (self.site_name, self.date)
            self.file_path = os.path.join(self.export_path, self.file_name)

    def __str__(self):
        """ Format used for report"""
        return ";".join([self.site_name, self.file_path, str(self.elapsed_time)])

    def already_downloaded(self):
        path = Path(self.export_path)

        return [str(file_path) for file_path in path.glob("%s_export*" % self.site_name)]

    def download_site(self):
        # do not download twice if not --force
        existing = self.already_downloaded()
        if existing and not self.force:
            logging.warning("%s already downloaded %sx. Last one is %s",
                            self.site_name, len(existing), self.file_path)
            return self.file_path

        # pepare query
        params = self.DWLD_GET_PARAMS.copy()
        params['sitebox'] = self.site_name

        # set timer to measure execution time
        start_time = timer()

        # make query
        logging.debug("downloading %s...", self.file_name)
        response = self.session.post(
            "%s/%s/%s" % (self.HOST, self.DWLD_URI, self.file_name),
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
                    expected_size=(int(total_length) / 4096) + 1)
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
        end_time = timer()
        self.elapsed_time = round(end_time - start_time)
        logging.info("file downloaded in %s", self.elapsed_time)
        tracer_path = os.path.join(self.output_path, self.TRACER)
        with open(tracer_path, 'a') as tracer:
            tracer.write(str(self))
            tracer.flush()

        # return PosixPath converted to string
        return self.file_path
