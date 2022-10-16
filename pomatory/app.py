from selenium import webdriver

# def set_up(request):
#     """
#     Main function to set up the driver and the logger. Should run before any test
#     :param request: pytest request
#     :return: -
#     """
#     preferred_browser = str(read_config()['browser'])
#     global driver
#     global logger
#
#     if preferred_browser == 'chrome':
#         chrome_options = webdriver.ChromeOptions()
#
#         # add argument options in order not to get WebDriverException: unknown error: DevToolsActivePort file doesn't
#         # exist while trying to initiate Chrome Browser
#         chrome_options.add_argument('--no-sandbox')
#         chrome_options.add_argument('--disable-dev-shm-usage')
#         chrome_options.add_argument('--remote-debugging-port=9222')
#         driver = webdriver.Chrome(options=chrome_options)
#
#     elif preferred_browser == 'firefox':
#         driver = webdriver.Firefox()
#     elif preferred_browser == 'edge':
#         driver = webdriver.Edge()
#     else:
#         logging.error("Please provide one of the supported browsers. Options: chrome, firefox, edge")
#
#     driver.set_page_load_timeout(20)
#     driver.implicitly_wait(5)
#     driver.get(read_config()["start_url"])
#     driver.maximize_window()
#
#     if request.cls is not None:
#         request.cls.driver = driver
#         request.cls.logger = logging
#         logger = logging
#
#     yield driver
#
#     # cleaning up after the test suite run
#     driver.quit()


def main_menu():
    print('Type "help", "exit", "configure"')
    while True:
        command, *arguments = input('~ ').split(' ')
        if len(command) > 0:
            if command.lower() == 'exit':
                break
            elif command.lower() == 'help':
                print('This is help.')
            elif command.lower() == 'configure':
                print('configure')
            elif command.lower() == 'add':
                print(sum(map(int, arguments)))
            else:
                print('Unknown command')


if __name__ == "__main__":
    main_menu()
