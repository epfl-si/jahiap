"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os
import csv
import logging

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
    def get_content_of_csv_file(file_path):
        """
        Get content of csv file 'filename'.
        """
        with open(file_path, newline='') as csvfile:
            has_header = csv.Sniffer().has_header(csvfile.read(1024))

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            rows = list(reader)

        logging.debug("Parsed CSV %s", rows)
        if has_header:
            return rows[1:]
        return rows[1:]

    @staticmethod
    def validate_dir(path, force_create=False):
        """
        Checks that the path exists and creates directories if necessary.
        """
        if not os.path.isdir(path):
            if force_create:
                os.makedirs(path)
                logging.info("created output dir %s", path)
            else:
                raise SystemExit("'%s' does not exist. Please create it first or use --force" % path)
        return True

    @staticmethod
    def validate_composition(path):
        """
        Checks if there is a docker-compose.yml file in this path
        """
        if not os.path.isdir(path):
            return False

        compose_path = os.path.join(path, "docker-compose.yml")
        if not os.path.isfile(compose_path):
            return False

        return True

    @classmethod
    def docker_compose(cls, path, up=True):
        """
        Start all containers if up is True.
        Stops containers and removes containers, networks, volumes, and images if up is False.
        """
        project = project_from_options(path, cls.DOCKER_OPTIONS)
        cmd = TopLevelCommand(project)
        if up: cmd.up(cls.DOCKER_OPTIONS)
        else: cmd.down(cls.DOCKER_OPTIONS)

        return cmd

    @classmethod
    def docker(cls, args, up=True):

        # check build dir
        cls.validate_dir(args['<BUILD_PATH>'], args['--force'])

        if args['--recurse']:
            for path in os.listdir(args['<BUILD_PATH>']):

                # only proceed with directories that contain a docker-compose
                full_path = os.path.join(args['<BUILD_PATH>'], path)
                if not cls.validate_composition(full_path):
                    continue

                # Secondly, start the container
                cls.docker_compose(full_path, up=up)
        else:
            if not cls.validate_composition(args['<BUILD_PATH>']):
                logging.error(
                    "%s does not contain a docker-compose-yml file",
                    args['<BUILD_PATH>'])
                return
            cmd = cls.docker_compose(args['<BUILD_PATH>'], up=up)
            if args['--debug']:
                cmd.logs(cls.DOCKER_OPTIONS)
