from selenium.webdriver.common.by import By
from selenium import webdriver

locator_types = {
    "id": By.ID,
    "xpath": By.XPATH,
    "name": By.NAME
}


def get_list_of_elements(driver: webdriver, locator: str, locator_type: str = "id") -> list:
    """
    Finds all elements that have the specific locator and returns them as a list
    :param driver: the webdriver to use
    :param locator: any type of locator
    :param locator_type: locator_type supported are described in locator_types dict
    :return: a list with all elements that can be found with the specific locator
    """
    return driver.find_elements(by=locator_types[locator_type], value=locator)


def get_text_of_elements(driver: webdriver, locator: str, locator_type: str = "id") -> list:
    """
    Finds all element texts that have the specific locator and returns them as a list
    :param driver: the webdriver to use
    :param locator: any type of locator
    :param locator_type: locator_type supported are described in locator_types dict
    :return: a list with all texts that can be found with the specific locator. "0" if no texts found
    """
    elements = driver.find_elements(by=locator_types[locator_type], value=locator)
    elements_names = []
    for element in elements:
        if element.text:
            elements_names.append(element.text)

    return elements_names if elements_names else ['0']


def get_current_url(driver: webdriver) -> str:
    """
    Gets the current url from the web driver provided
    :param driver: the webdriver to use
    :return: a str with the current url
    """
    return driver.current_url
