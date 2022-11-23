import os
import sys
import argparse
from pomatory.pomatory import Pomatory


def main():
    parser = argparse.ArgumentParser(prog='POMatory',
                                     description='Welcome to POMatory!'
                                                 ' A tool to help you automate the boring work of locating '
                                                 'elements in a web page for your Automation Framework according'
                                                 ' to the POM architecture')
    parser.add_argument('-t', '--types',
                        dest='html_element_to_look_for_ids',
                        choices=['[\'input\', \'button\']'],
                        default=['input', 'button'],
                        help='Types of html elements to look for. '
                        )
    parser.add_argument('--url',
                        dest='base_url',
                        help='URL to start looking for locators.',
                        required=True,
                        type=str
                        )
    parser.add_argument('-b', '--browser',
                        dest='browser',
                        help='Browser to use for the selenium navigation. '
                             'Available options: chrome, firefox. '
                             'default: firefox',
                        choices=['firefox', 'chrome'],
                        default="firefox",
                        type=str
                        )

    parser.add_argument('-d', '--destination_path',
                        dest='save_path',
                        help='[Optional] The path for the newly created file(s). Default: current',
                        required=False,
                        default=os.getcwd(),
                        type=str
                        )
    parser.add_argument('-s', '--single_entries',
                        dest='single_locator',
                        help='The output of the locators. True for one line entries. False for dict with all '
                             'locators for a specific web element. Default: True',
                        default=True,
                        type=bool
                        )

    # TODO: part of log improvement. maybe combine the 2 next arguments
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        default=False,
                        help='Verbose Output. '
                             'default: False.'
                        )
    parser.add_argument('-q', '--quiet',
                        dest='quiet',
                        default=False,
                        help='Suppress Output. '
                             'default: False.'
                        )
    # TODO: part of the standalone version
    parser.add_argument('-w', '--web_driver',
                        dest='web_driver_download',
                        help='Whether to try to download the appropriate webdriver for the specified browser. '
                             'default: False',
                        default=False,
                        type=bool
                        )
    # TODO: needed for standalone version
    parser.add_argument('-u', '--username',
                        dest='username',
                        help='[Optional] Username to login. ',
                        required=False,
                        type=str
                        )
    # TODO: needed for standalone version
    parser.add_argument('-p', '--password',
                        dest='password',
                        help='[Optional] Password to login. ',
                        required=False,
                        type=str
                        )

    if not parser.parse_args().base_url:
        sys.stderr.write("Please provide a starting url for POMatory")
        sys.exit(1)

    Pomatory(save_path=parser.parse_args().save_path,
             return_single=parser.parse_args().single_locator,
             types=parser.parse_args().html_element_to_look_for_ids,
             url=parser.parse_args().base_url,
             browser=parser.parse_args().browser,
             username=parser.parse_args().username,
             password=parser.parse_args().password,
             verbose=parser.parse_args().verbose,
             quiet=parser.parse_args().quiet
             )


def clean_up(driver_functions):
    # TODO: add more cleanup routines
    driver_functions.quit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # TODO: add call to clean_up()
        sys.stderr.write("User interrupt!\n")
        sys.exit(0)
