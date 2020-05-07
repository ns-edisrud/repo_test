import logging

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class WorkbookPage(SigninPage):
    """
    Page object for the sign in page.

    URL:
        /signin

    """

    locators = {
        "edit_tab": (By.ID, "edit-ToolbarButton"),
    }

    def click_tab(self, ctx: Context, tab_name):
        """Click a specified tab on the workbook page.

        Args:
            ctx: The behave context object.
            tab_name: The name of the tab to click on

        """
        import pdb; pdb.set_trace()
        ClickFunctions.click_element_by_name(ctx, self.locators, tab_name)
