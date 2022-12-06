# POMatory
Automatically find locators for web elements that can be used in selenium projects

## Installation
2 ways to use POMatory: 
 - Import POMatory as a library in your code
 - [_WIP: bugs lurking_] Install POMatory locally with `pip install .`.Then run it with `pomatory` and  
by passing any desired __Running Arguments__

### Running Arguments

  - __-t [--types]__ HTML_ELEMENT_TO_LOOK_FOR_IDS: Types of html elements to look for.
  - __[--url]__ BASE_URL: URL to start looking for locators.
  - __-b [--browser]__ BROWSER: Browser to use for the selenium navigation. Available options: chrome, firefox. default: firefox
  - __-u [--username]__ USERNAME: *[Optional]* Username to login.
  - __-p [--password]__ PASSWORD: *[Optional]* Password to login.
  - __-d [--destination_path]__ SAVE_PATH: *[Optional]* The path for the newly created file(s). Default: current
  - __-s [--single_entries]__ SINGLE_LOCATOR: The output of the locators. True for one line entries. False for dict with all locators for a specific web element. Default: True
  - __-v [--verbose]__ VERBOSE: Verbose Output. default: False.
  - __-q [--quiet]__ QUIET: Suppress Output. default: False.
  - __-w [--web_driver]__ WEB_DRIVER_DOWNLOAD: Whether to try to download the appropriate webdriver for the specified browser. default: False
