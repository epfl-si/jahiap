"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import csv
import logging


class Utils:

    @staticmethod
    def get_content_of_csv_file(file_path):
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
