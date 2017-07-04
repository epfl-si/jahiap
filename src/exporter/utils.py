"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
class Utils:

    @staticmethod
    def escape_quotes(str):
        return str.replace('"', '\\"')

    @staticmethod
    def get_menu_id(b):
        return b.decode("utf-8").replace('\n', '')
