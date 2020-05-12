import logging

from behave.runner import Context
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

from generic_behave.ns_selenium.selenium_functions.general_functions import GeneralFunctions
from generic_behave.ns_selenium.selenium_functions.wait_functions import WaitFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class WorkbookEditPage(SigninPage):
    """
    Page object for the workbook edit page.
    """

    locators = {
        "edit_story_button": (By.CLASS_NAME, "ns-edit"),
        "worksheet_toolbar": (By.CLASS_NAME, "worksheet-toolbar"),
        "extension_frame_5": (By.CLASS_NAME, "extension_frame_5"),
        "narrative_content": (By.ID, "narrative-content"),
    }

    def click_edit_story(self, ctx: Context) -> None:
        """
        Opens up the edit story modal.

        Args:
            ctx: The behave context object.

        """
        #  wait for the iframe to be present
        WaitFunctions.wait_for_presence_of_frame_then_switch(ctx, 'extension_frame_5')
        # wait for content to be present
        WaitFunctions.wait_for_presence_of_element(ctx, self.locators, "narrative_content")
        # click the edit story button twice
        action = webdriver.common.action_chains.ActionChains(ctx.driver)
        action.move_to_element(GeneralFunctions.get_element_by_name(ctx, self.locators, "edit_story_button"))
        action.click()
        # pause to accept second click
        time.sleep(1)
        action.click()
        action.perform()
        GeneralFunctions.switch_to_active_window(ctx, 1)
