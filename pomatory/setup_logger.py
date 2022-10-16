import logging


log_format = (
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('default_logger')
