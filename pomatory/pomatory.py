import logging
from pomatory.locators import Locators as Loc
from pomatory.webdriver_functions import WebDriverFunctions as webDriver
from pomatory.logger import Logger
import os


class Pomatory:

    def __init__(self, driver=None, save_path=os.getcwd(), return_single=True, log_level=logging.DEBUG, check_ids=True,
                 types=None, url=None, browser="firefox", username=None, password=None, verbose=False, quiet=False):
        if types is None:
            types = ['input', 'button']

        self.save_path = save_path
        self.types = types
        self.url = url  # webdriver related
        self.browser = browser  # webdriver related
        self.logger = self._setup_logger(log_level=log_level, verbose=verbose, quiet=quiet)
        self.return_single = return_single
        self.check_ids = check_ids
        self.username = username  # webdriver related
        self.password = password  # webdriver related

        if driver:
            self.driver_instance = webDriver(logger=self.logger, web_driver=driver)
        else:
            self.driver_instance = webDriver(logger=self.logger, args={"browser": self.browser, "url": self.url})

    def find_locators(self):
        loc = Loc(log=self.logger, driver_instance=self.driver_instance)
        loc.find_locators(check_ids=self.check_ids, save_path=self.save_path, return_single=self.return_single,
                          html_element_types=self.types)

    @staticmethod
    def _setup_logger(log_level=logging.INFO, verbose=False, quiet=False):
        """
        TODO: add logic for better logging here
        :param log_level:
        :param verbose:
        :param quiet:
        :return:
        """
        if not log_level:
            if verbose:
                log_level = logging.DEBUG
            elif quiet:
                log_level = logging.CRITICAL
        return Logger(log_level=log_level)
