import logging
import pomatory.locators as loc
import os


class Pomatory:

    def __init__(self, driver, folder_path=os.getcwd(), return_single=True, log_level=logging.DEBUG):
        self.driver = driver
        self.folder_path = folder_path
        self.return_single = return_single
        self.log_level = log_level

    def find_locators(self):
        loc.find_locators(webdriver=self.driver, folder_path=self.folder_path, return_single=self.return_single)


