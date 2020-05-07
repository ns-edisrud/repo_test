import logging

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class WorkbookEditPage(SigninPage):
    """
    Page object for the sign in page.

    URL:
        /signin

    """