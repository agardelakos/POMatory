from selenium.webdriver.common.by import By
from selenium import webdriver

# TODO: add more options (e.g. CSS_SELECTOR)
locator_types = {
    "id": By.ID,
    "xpath": By.XPATH,
    "name": By.NAME
}


class WebDriverFunctions:
    driver = webdriver

    def __init__(self, logger, web_driver=None, args=None):

        self.logger = logger
        if web_driver:
            self.driver = web_driver
        else:
            self._set_up_webdriver(args)

    def _set_up_webdriver(self, args):
        if args.get("browser") == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            # chrome_options.add_argument('--remote-debugging-port=9222')
            self.driver = webdriver.Chrome(options=chrome_options)

        elif args.get("browser") == 'firefox':
            self.driver = webdriver.Firefox()
        # TODO: add edge support
        # elif preferred_browser == 'edge':
        #     driver = webdriver.Edge()
        else:
            self.logger.error("Please provide one of the supported browsers. Options: chrome, firefox")

        self.driver.set_page_load_timeout(20)
        self.driver.implicitly_wait(5)
        self.driver.get(str(args.get("url")))
        self.driver.maximize_window()

        # TODO: needed for standalone version
        # if request.cls is not None:
        #     request.cls.driver = driver
        #     request.cls.logger = logging
    def get_list_of_elements(self, locator: str, locator_type: str = "id") -> list:
        """
        Finds all elements that have the specific locator and returns them as a list

        :param locator: any type of locator
        :param locator_type: locator_type supported are described in locator_types dict
        :return: a list with all elements that can be found with the specific locator
        """
        return self.driver.find_elements(by=locator_types[locator_type], value=locator)

    def get_text_of_elements(self, locator: str, locator_type: str = "id") -> list:
        """
        Finds all element texts that have the specific locator and returns them as a list

        :param locator: any type of locator
        :param locator_type: locator_type supported are described in locator_types dict
        :return: a list with all texts that can be found with the specific locator. "0" if no texts found
        """
        elements = self.driver.find_elements(by=locator_types[locator_type], value=locator)
        elements_names = []
        for element in elements:
            if element.text:
                elements_names.append(element.text)

        return elements_names if elements_names else ['0']

    def get_current_url(self) -> str:
        """
        Gets the current url from the web driver provided

        :return: a str with the current url
        """
        return self.driver.current_url
