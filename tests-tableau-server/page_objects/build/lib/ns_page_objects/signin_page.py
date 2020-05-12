import logging
import json

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from generic_behave.ns_selenium.selenium_functions.input_functions import InputFunctions

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class SigninPage:
    """
    Page object for the sign in page.

    URL:
        /signin

    """

    locators = {
        "back_to_content": (By.CLASS_NAME, "tb-empty-state-button"),
        "login_button": (By.CLASS_NAME, "tb-button-login"),
        "email_input": (By.NAME, "username"),
        "password_input": (By.NAME, "password"),
    }

    def __init__(self, ctx: Context) -> None:
        """Give page object subclasses access to context and driver objects.

        Args:
            ctx: The behave context object.

        """
        self.ctx = ctx
        self.driver = self.ctx.driver

    def log_in(self, ctx: Context):
        """Log in as the given user.

        Args:
            ctx: The behave context object.

        """
        email = json.loads(ctx.users)['username']
        password = json.loads(ctx.users)['password']
        InputFunctions.send_keys_to_element_by_name(
            self.ctx, self.locators, "email_input", email
        )
        InputFunctions.send_keys_to_element_by_name(
            self.ctx, self.locators, "password_input", password
        )
        ClickFunctions.click_element_by_name(ctx, self.locators, "login_button")
        ClickFunctions.click_element_by_name(ctx, self.locators, "back_to_content")
