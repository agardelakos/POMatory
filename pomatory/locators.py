import os
import re
from bs4 import PageElement
from bs4 import BeautifulSoup
from pomatory.logger import Logger


class Locators:
    def __init__(self, log: Logger = None, driver_instance=None):
        self.driver_inst = driver_instance
        self.logger = log.logger
        self.driver = self.driver_inst.driver

    # TODO: add logic for return_single
    def find_locators(self, check_ids: bool = True, html_element_types: list = None, save_path: str = "",
                      return_single: bool = False):

        if html_element_types is None:
            # TODO: needs refactoring in order to search for 'div' as well.
            html_element_types = ['input', 'button']  # , 'div']

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        id_list = {}

        # finding IDs
        if check_ids:
            id_list = self._retrieve_ids(html_element_types, soup)
            self.logger.info(f"ID_list: {str(id_list)}")

        # finding/constructing xpaths
        xpaths_list = self._retrieve_xpaths(html_element_types, soup)
        self.logger.info(f"XPATHs_list: {str(xpaths_list)}")

        # Writing to file
        self._write_to_python_file(locator_dict={"id": id_list, "xpath": xpaths_list},
                                   file_name=self._format_filename(self.driver_inst.get_current_url()),
                                   save_path=save_path)

    def _retrieve_ids(self, html_element_to_look_for_ids, soup) -> list:
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
                        if self._is_unique_locator(tag['id'], 'id'):
                            id_list.append(tag['id'])
                            self.logger.info(f"ID for element: {el} found={str(tag['id'])}")
                except KeyError:
                    self.logger.info(f"No key found for: {el}")
        return id_list

    def _retrieve_xpaths(self, html_element_to_look_for_ids, soup) -> list:
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
                elem, parent, parent_type = self._construct_xpath_locator(web_element=tag, locator_string=tag['class'],
                                                                          element_type=el)

                if self._is_unique_locator(locator=elem, locator_type="xpath"):
                    xpaths_list.append(elem)
                else:
                    number_of_multiple_elements = 1
                    self.logger.debug("Searching for unique locator by trying to add text of the element...")
                    text_elements = self.driver_inst.get_text_of_elements(locator=elem, locator_type="xpath")
                    if text_elements == ['0']:
                        self.logger.debug("Could not find text for the elements")
                    else:
                        number_of_multiple_elements = len(text_elements)

                        if text_elements:
                            self.logger.debug("Trying Adding name")
                            for text in text_elements:
                                temp_xpath = elem + self._add_contains_text(text)
                                if self._is_unique_locator(locator=temp_xpath,
                                                           locator_type="xpath") and temp_xpath not in xpaths_list:
                                    xpaths_list.append(temp_xpath)
                                    number_of_multiple_elements = number_of_multiple_elements - 1

                        if number_of_multiple_elements <= 0:
                            self.logger.debug("No need to check recursively")
                        else:
                            self.logger.debug("Could not find all elements with just adding the text")

                    if number_of_multiple_elements > 0:
                        self.logger.debug("Trying recursively with parents...")

                        elem = self._recursive_reverse_search_locators(web_element=tag, locator_string=elem,
                                                                       element_type=el,
                                                                       parent_locator_string=tag.findParent()['class'],
                                                                       parent_element_type=tag.findParent().name)
                        if elem:
                            xpaths_list.append(elem)
        return xpaths_list

    def _recursive_reverse_search_locators(self, locator_string: str, element_type: str, web_element: PageElement,
                                           parent_locator_string: str = None, parent_element_type: str = None) -> str:
        """

        @param locator_string:
        @param element_type:
        @param web_element:
        @param parent_locator_string:
        @param parent_element_type:
        :return:
        """

        xpath_to_check, par_el, par_type = self._construct_xpath_locator(web_element=web_element,
                                                                         locator_string=locator_string,
                                                                         element_type=element_type,
                                                                         parent_locator_string=parent_locator_string,
                                                                         parent_element_type=parent_element_type
                                                                         )
        reasons_to_break = ["//head", "//body", "//html"]

        if any(ele in str(locator_string) for ele in reasons_to_break):
            self.logger.info("Reached the top of the doc! Cannot find unique id")
            return ""
        elif self._is_unique_locator(locator=xpath_to_check, locator_type="xpath"):
            return locator_string
        else:
            try:
                par_loc_str = par_el.findParent()['class']
            except KeyError:
                par_loc_str = "0"
            return self._recursive_reverse_search_locators(web_element=par_el,
                                                           locator_string=xpath_to_check,
                                                           element_type=par_type,
                                                           parent_locator_string=par_loc_str,
                                                           parent_element_type=par_el.findParent().name
                                                           )

    def _construct_xpath_locator(self, web_element: PageElement, locator_string=None, element_type: str = "div",
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
            # logger.debug("son to string")
            locator_string = " ".join([str(item) for item in locator_string])

        if parent_locator_string:
            if isinstance(parent_locator_string, list):
                # logger.debug("parent to string")
                parent_locator_string = " ".join([str(item) for item in parent_locator_string])
            # logger.debug("yes parent")
            if parent_locator_string:
                # self.logger.debug("1")
                if parent_locator_string == '0':
                    res = "//{}".format(parent_element_type) + locator_string
                else:
                    res = xpath_locator_format.format(parent_element_type, parent_locator_string) + locator_string
            else:
                # logger.debug("2")
                res = "//{}{}".format(parent_element_type, locator_string)
            parent_element = web_element.find_parent()
        else:
            # logger.debug("no parent.")
            if locator_string:
                # logger.debug("3")
                res = xpath_locator_format.format(element_type, locator_string)
            else:
                # logger.debug("4")
                res = "//{}".format(element_type)
        self.logger.debug(res)
        return res, parent_element, parent_element_type

    def _is_unique_locator(self, locator: str, locator_type: str = 'id') -> bool:
        """
        Checks if the provided locator identifies uniquely a web element
        @param locator: any type of locator
        @param locator_type: locator_type supported are described in locator_types dict in webdriver_functions.py
        :return:
        """
        if len(self.driver_inst.get_list_of_elements(locator, locator_type)) == 1:
            self.logger.info(f"element with locator: {locator} and locator_type: {locator_type} is unique.")
            return True
        else:
            self.logger.info(f"element with locator: {locator} and locator_type: {locator_type} is NOT unique.")
            return False

    def _format_filename(self, text: str) -> str:
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
                self.logger.debug(f"discarded: {part}")
            else:
                self.logger.debug(f"valid part: {part}")
                filename_parts_valid.append(str(part))
        if len(filename_parts_valid) == 0:
            filename = "home_page"
        else:
            filename = ""
            for s in filename_parts_valid:
                filename = filename + "{}_".format((str(s)))
            self.logger.info(f"Created file: {filename}")

        filename = filename.replace(' ', '_')
        return filename + "page"

    @staticmethod
    def _to_camel_case(text: str) -> str:
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

    def _create_file(self, filename: str = "", file_path: str = "") -> str:
        """
        Creates a .py file with the provided file name
        @param filename: name of the file to be created. If it already exists adds _.
        TODO: maybe remove and instead write to the existing file
        :return: a str with the path of the file (including the ending of the file)
        """
        from os.path import exists

        try:
            if file_path is None:
                cur_file_path = os.path.dirname(os.path.abspath(__file__))
            else:
                cur_file_path = file_path
            path = os.path.join(cur_file_path, filename)
            while exists(path + ".py"):
                path = path + "_"
            self.logger.info("Created file: {}".format(str(path) + ".py"))
            return path + ".py"

        except Exception as e:
            self.logger.error(f"Failed to create file: {filename}. {str(e)}")

    def _write_to_python_file(self, locator_dict: dict, file_name: str, save_path: str = os.getcwd()):
        """
        Creates and write the locator dictionary to a file with ending .py
        @param locator_dict: all the locators that are meant to be written to the file
        @param file_name: name of the file to create. Can be path to file + name
        @parm save_path: directory for the output file to be saved
        :return: nothing
        """

        python_file_template = "\"\"\" {0} Locators \"\"\"\n"

        locator_template = "_{0}_{1} = \"{2}\"\n"
        file_path = os.path.join(save_path, self._create_file(filename=file_name, file_path=save_path))
        with open(file_path, "a") as file_to_write:
            if len(locator_dict) > 0:
                for locator_type in locator_dict:
                    file_to_write.write(python_file_template.format(locator_type))
                    for element in locator_dict[locator_type]:
                        # TODO: add better locator naming
                        file_to_write.write(
                            locator_template.format(re.sub(r"[^a-zA-Z0-9 ]", "", element).replace(' ', '_'),
                                                    locator_type, element))
            file_to_write.close()

    @staticmethod
    def _add_contains_text(text: str) -> str:
        """
        simple function to construct the contains text locator with the str provided
        @param text: the str to add to the locator
        :return: str with the proper format of the locator
        """
        return "[contains(text(), \'{}\')]".format(text)
