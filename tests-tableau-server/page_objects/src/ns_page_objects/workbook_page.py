import logging

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from generic_behave.ns_selenium.selenium_functions.general_functions import GeneralFunctions
from generic_behave.ns_selenium.selenium_functions.filter_functions import FilterFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class WorkbookPage(SigninPage):
    """
    Page object for the sign in page.
    """

    locators = {
        "edit_tab": (By.ID, "edit-ToolbarButton"),
        "sheet_button": (By.CLASS_NAME, "tabAuthSheetListItem"),
        "extension_button": (By.CLASS_NAME, "tabExtensionZoneObject"),
    }

    def click_tab(self, ctx: Context, tab_name) -> None:
        """Click a specified tab on the workbook page.

        Args:
            ctx: The behave context object.
            tab_name: The name of the tab to click on

        """
        ClickFunctions.click_element_by_name(ctx, self.locators, tab_name)

    def double_click_sheet_button(self, ctx: Context, sheet_name: str) -> None:
        """Double click a specified sheet button (possibly multiple instances) by name
        while setting up a dashboard on the workbook page.

        Args:
            ctx: The behave context object.
            sheet_name: The name of the sheet button to double click

        """
        sheet_list = GeneralFunctions.get_elements_by_name(ctx, self.locators, "sheet_button")
        LOGGER.debug(f'Attempting to double click on sheet: {sheet_name}')
        FilterFunctions.filter_and_click(sheet_list, sheet_name)
        FilterFunctions.filter_and_click(sheet_list, sheet_name)
        LOGGER.debug(f'Successfully double clicked on sheet: {sheet_name}')

    def double_click_button(self, ctx: Context, button_name) -> None:
        """Double click a specified button (one that does not have multiple instances) while setting
        up a dashboard on the workbook page.

        Args:
            ctx: The behave context object.
            button_name: The name of the button to double click

        """
        LOGGER.debug(f'Attempting to double click on button: {button_name}')
        ClickFunctions.click_element_by_name(ctx, self.locators, button_name)
        ClickFunctions.double_click(ctx, self.locators, button_name)
        LOGGER.debug(f'Successfully double clicked on sheet: {button_name}')
