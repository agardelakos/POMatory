import logging


class Logger:

    def __init__(self, log_level=logging.DEBUG):
        log_format = '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s'

        logging.basicConfig(level=log_level, format=log_format, filename='pomatory.log')
        self.logger = logging.getLogger('default_logger')
