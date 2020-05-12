import logging

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class WorkbookEditPage(SigninPage):
    """
    Page object for the workbook edit page.
    """

    locators = {
        "edit_story_button": (By.CLASS_NAME, "ns-edit"),
    }

    def click_edit_story(self, ctx: Context) -> None:
        """
        Opens up the edit story modal.

        Args:
            ctx: The behave context object.

        """
        ctx. driver.switch_to.frame('extension_frame_5')
        # ctx.driver.switchTo().frame("extension_frame_5")
        # ClickFunctions.click_element_by_name(ctx, self.locators, "edit_story_button")
