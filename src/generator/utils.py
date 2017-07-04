"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import csv
import logging
import os

from compose.cli.main import TopLevelCommand, project_from_options


class Utils:

    DOCKER_OPTIONS = {
        "--no-deps": False,
        "--abort-on-container-exit": False,
        "SERVICE": "",
        "--remove-orphans": False,
        "--no-recreate": True,
        "--force-recreate": False,
        "--build": False,
        '--no-build': False,
        '--no-color': False,
        "--rmi": "none",
        "--volumes": "",
        "--follow": False,
        "--timestamps": False,
        "--tail": "all",
        "--scale": [],
        "-d": True,
    }

    @staticmethod
    def csv_to_list(file_path):
        """
        Get content of csv file 'filename'.
        """
        with open(file_path, newline='') as csvfile:
            has_header = csv.Sniffer().has_header(csvfile.read(1024))
            csvfile.seek(0)  # rewind
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            if has_header:
                next(reader)  # skip header row
            rows = list(reader)

            logging.debug("Parsed CSV %s", rows)
            return rows

    @staticmethod
    def csv_to_dict(file_path):

        sites = []
        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sites.append(row)
        return sites

    @staticmethod
    def validate_dir(path, force_create=False):
        if not os.path.isdir(path):
            if force_create:
                os.makedirs(path)
                logging.info("created output dir %s", path)
            else:
                raise SystemExit("'%s' does not exist. Please create it first or use --force" % path)
        return True

    @staticmethod
    def validate_composition(path):
        if not os.path.isdir(path):
            return False

        compose_path = os.path.join(path, "docker-compose.yml")
        if not os.path.isfile(compose_path):
            return False

        return True

    @classmethod
    def docker(cls, path, up=True):

        project = project_from_options(path, cls.DOCKER_OPTIONS)
        cmd = TopLevelCommand(project)
        if up:
            cmd.up(cls.DOCKER_OPTIONS)
        else:
            cmd.down(cls.DOCKER_OPTIONS)

        return cmd
