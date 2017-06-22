"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import csv


class Utils:

    @staticmethod
    def get_content_of_csv_file(filename):
        """
        Get content of csv file 'filename'.
        """
        rows = []

        # Create a sites list
        # [{name:'dcsl', parent:'labs', type:'site' }, {...}, ...]
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
        return rows
