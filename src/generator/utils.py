"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import csv
import logging


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
