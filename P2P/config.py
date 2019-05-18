import configparser
import io

from P2P.constants import *


class Config:

    def __init__(self):
        pass

    def load_config(self):
        """
            load config file.

            function that reads configuration file and its parameters

            Returns
            -------
            str
                RTT, F and X

        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        return int(config['loss simulation']['RTT']), config['loss simulation']['F'], config['loss simulation']['X']
