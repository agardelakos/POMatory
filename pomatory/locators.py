import os
import re
from bs4 import PageElement
from bs4 import BeautifulSoup
import pomatory.selenium_functions as sf
from pomatory.setup_logger import logger

driver = None


def find_locators(webdriver, check_ids=False, folder_path=os.getcwd(), return_single=False,
                  html_element_to_look_for_ids=None):
    if html_element_to_look_for_ids is None:
        # TODO: needs refactoring in order to search for 'div' as well.
        html_element_to_look_for_ids = ['input', 'button']  # , 'div']

    global driver
    driver = webdriver
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    id_list = {}

    if check_ids:
        id_list = retrieve_ids(html_element_to_look_for_ids, soup)
        logger.info(f"ID_list: {str(id_list)}")

    # """ finding/constructing xpaths"""
    xpaths_list = retrieve_xpaths(html_element_to_look_for_ids, soup)
    logger.info(f"XPATHs_list: {str(xpaths_list)}")

    write_to_python_file(locator_dict={"id": id_list, "xpath": xpaths_list},
                         file_name=format_filename(sf.get_current_url(driver)))


def retrieve_ids(html_element_to_look_for_ids, soup) -> list:
    """
    Finding ids
    @param html_element_to_look_for_ids:
    @param soup:
    :return: list with ids
    """
    id_list = []

    for el in html_element_to_look_for_ids:
        tags = soup.find_all(el)
        for tag in tags:
            try:
                if tag['id']:
                    if is_unique_locator(tag['id'], 'id'):
                        id_list.append(tag['id'])
                        logger.info(f"ID for element: {el} found={str(tag['id'])}")
            except KeyError:
                logger.info(f"No key found for: {el}")
    return id_list


def retrieve_xpaths(html_element_to_look_for_ids, soup) -> list:
    """
    Finding/constructing xpaths

    @param html_element_to_look_for_ids:
    @param soup:
    :return: list with xpaths
    """
    xpaths_list = []
    for el in html_element_to_look_for_ids:
        tags2 = soup.find_all(name=el, attrs={'id': None, 'class': re.compile("^null|$")})

        for tag in tags2:
            elem, parent, parent_type = construct_xpath_locator(web_element=tag, locator_string=tag['class'],
                                                                element_type=el)

            if is_unique_locator(locator=elem, locator_type="xpath"):
                xpaths_list.append(elem)
            else:
                number_of_multiple_elements = 1
                logger.debug("Searching for unique locator by trying to add text of the element...")
                text_elements = sf.get_text_of_elements(driver=driver, locator=elem, locator_type="xpath")
                if text_elements == ['0']:
                    logger.debug("Could not find text for the elements")
                else:
                    number_of_multiple_elements = len(text_elements)

                    if text_elements:
                        logger.debug("Trying Adding name")
                        for text in text_elements:
                            temp_xpath = elem + add_contains_text(text)
                            if is_unique_locator(locator=temp_xpath,
                                                 locator_type="xpath") and temp_xpath not in xpaths_list:
                                xpaths_list.append(temp_xpath)
                                number_of_multiple_elements = number_of_multiple_elements - 1

                    if number_of_multiple_elements <= 0:
                        logger.debug("No need to check recursively")
                    else:
                        logger.debug("Could not find all elements with just adding the text")

                if number_of_multiple_elements > 0:
                    logger.debug("Trying recursively with parents...")

                    elem = recursive_reverse_search_locators(web_element=tag, locator_string=elem,
                                                             element_type=el,
                                                             parent_locator_string=tag.findParent()['class'],
                                                             parent_element_type=tag.findParent().name)
                    if elem:
                        xpaths_list.append(elem)
    return xpaths_list


def recursive_reverse_search_locators(locator_string: str, element_type: str, web_element: PageElement,
                                      parent_locator_string: str = None, parent_element_type: str = None) -> str:
    """

    @param locator_string:
    @param element_type:
    @param web_element:
    @param parent_locator_string:
    @param parent_element_type:
    :return:
    """

    xpath_to_check, par_el, par_type = construct_xpath_locator(web_element=web_element,
                                                               locator_string=locator_string,
                                                               element_type=element_type,
                                                               parent_locator_string=parent_locator_string,
                                                               parent_element_type=parent_element_type
                                                               )
    reasons_to_break = ["//head", "//body", "//html"]

    if any(ele in str(locator_string) for ele in reasons_to_break):
        logger.info("Reached the top of the doc! Cannot find unique id")
        return ""
    elif is_unique_locator(locator=xpath_to_check, locator_type="xpath"):
        return locator_string
    else:
        try:
            par_loc_str = par_el.findParent()['class']
        except KeyError:
            par_loc_str = "0"
        return recursive_reverse_search_locators(web_element=par_el,
                                                 locator_string=xpath_to_check,
                                                 element_type=par_type,
                                                 parent_locator_string=par_loc_str,
                                                 parent_element_type=par_el.findParent().name
                                                 )


def construct_xpath_locator(web_element: PageElement, locator_string=None, element_type: str = "div",
                            parent_locator_string="", parent_element_type: str = "div"):
    """
    Constructs a str ready to be written to file
    @param web_element:
    @param parent_element_type: the parent's WebElement type (e.g. div, button, input)
    @param parent_locator_string: can be list or str. to be added on the front of the xpath with the usual format
    @param locator_string: the str for the class. can be list or single str. Will add this in the usual format of
    locators
    @param element_type: the WebElement type (e.g. div, button, input)
    :return: A str and a PageElement of the parent with that is ready to be used as a locator
    """
    xpath_locator_format = "//{}[@class=\'{}\']"
    parent_element = None
    if isinstance(locator_string, list):
        logger.debug("son to string")
        locator_string = " ".join([str(item) for item in locator_string])

    if parent_locator_string:
        if isinstance(parent_locator_string, list):
            logger.debug("parent to string")
            parent_locator_string = " ".join([str(item) for item in parent_locator_string])
        logger.debug("yes parent")
        if parent_locator_string:
            logger.debug("1")
            if parent_locator_string == '0':
                res = "//{}".format(parent_element_type) + locator_string
            else:
                res = xpath_locator_format.format(parent_element_type, parent_locator_string) + locator_string
        else:
            logger.debug("2")
            res = "//{}{}".format(parent_element_type, locator_string)
        parent_element = web_element.find_parent()
    else:
        logger.debug("no parent.")
        if locator_string:
            logger.debug("3")
            res = xpath_locator_format.format(element_type, locator_string)
        else:
            logger.debug("4")
            res = "//{}".format(element_type)
    logger.debug(res)
    return res, parent_element, parent_element_type


def is_unique_locator(locator: str, locator_type: str = 'id') -> bool:
    """
    Checks if the provided locator identifies uniquely a web element
    @param locator: any type of locator
    @param locator_type: locator_type supported are described in locator_types dict in selenium_functions.py
    :return:
    """
    global driver
    if len(sf.get_list_of_elements(driver, locator, locator_type)) == 1:
        logger.info("element with locator: {} and locator_type: {} is unique.".format(locator, locator_type))
        return True
    else:
        logger.info(
            "element with locator: {} and locator_type: {} is NOT unique.".format(locator, locator_type))
        return False


def format_filename(text: str) -> str:
    """
    Takes a string (intended use is url) and returns a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are removed.
    Also, spaces are replaced with underscores. TODO: duplicate from to_camel_case()?
    @param text: str to format
    :return: a str that is ready to be used as a filename TODO: move concat of 'page' elsewhere
    """
    filename_parts = text.split('/')
    filename_parts_valid = []
    for part in filename_parts:
        if part.startswith("https") or not part or part.__contains__(".") or any(c.isdigit() for c in part):
            logger.info("discarded: {}".format(part))
        else:
            logger.info("valid part: {}".format(part))
            filename_parts_valid.append(str(part))
    if len(filename_parts_valid) == 0:
        filename = "home_page"
    else:
        filename = ""
        for s in filename_parts_valid:
            filename = filename + "{}_".format((str(s)))
        logger.info("created: {}".format(filename))

    filename = filename.replace(' ', '_')
    return filename + "page"


def to_camel_case(text: str) -> str:
    """
    Replaces the '-' character to '_' and returns the text in came case format
    @param text: the text to change
    :return: str in the camel case format
    """
    s = text.replace("-", " ").replace("_", " ")
    s = s.split()
    if len(text) == 0:
        return text
    return ''.join(i.capitalize() for i in s[0:])


def create_file(filename: str = "") -> str:
    """
    Creates a .py file with the provided file name
    @param filename: name of the file to be created. If it already exists adds _.
    TODO: maybe remove and instead write to the existing file
    :return: a str with the path of the file (including the ending of the file)
    """
    from os.path import exists

    try:
        cur_file_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(cur_file_path, filename)
        while exists(path + ".py"):
            path = path + "_"
        logger.info("Created file: {}".format(str(path) + ".py"))
        return path + ".py"

    except Exception as e:
        logger.error("Failed to create file: {}. {}".format(filename, str(e)))


def write_to_python_file(locator_dict: dict, file_name: str, class_to_inherit_from: str = ""):
    """
    Creates and write the locator dictionary to a file with ending .py
    @param locator_dict: all the locators that are meant to be written to the file
    @param file_name: name of the file to create
    @param class_to_inherit_from: TODO: probably delete
    :return: nothing
    """
    # TODO: think if we should add import for the class to inherit from
    if class_to_inherit_from:
        python_file_template = "class {0}({1}):\n    \"\"\"Locators \"\"\"\n".format(to_camel_case(file_name),
                                                                                     class_to_inherit_from)
    else:
        python_file_template = "class {0}:\n    \"\"\"Locators \"\"\"\n".format(to_camel_case(file_name))

    locator_template = "    _{0}_{1} = \"{2}\"\n"

    with open(create_file(file_name), "a") as fileToWrite:
        fileToWrite.write(python_file_template)
        if len(locator_dict) > 0:
            for locator_type in locator_dict:
                for element in locator_dict[locator_type]:
                    # TODO: add better locator naming
                    fileToWrite.write(
                        locator_template.format(re.sub(r"[^a-zA-Z0-9 ]", "", element).replace(' ', '_'),
                                                locator_type, element))
        fileToWrite.close()


def add_contains_text(text: str) -> str:
    """
    simple function to construct the contains text locator with the str provided
    @param text: the str to add to the locator
    :return: str with the proper format of the locator
    """
    return "[contains(text(), \'{}\')]".format(text)
