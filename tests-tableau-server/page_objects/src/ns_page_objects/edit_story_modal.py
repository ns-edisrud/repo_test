import logging

from behave.runner import Context
from selenium.webdriver.common.by import By

from generic_behave.ns_selenium.selenium_functions.click_functions import ClickFunctions
from generic_behave.ns_selenium.selenium_functions.input_functions import InputFunctions
from .signin_page import SigninPage

# Initialize a logger
LOGGER = logging.getLogger(__name__)


class EditStoryModal(SigninPage):
    """
    Page object for the edit story modal.
    """

    locators = {
        "add_custom_story_item": (By.CLASS_NAME, "add-bullet-btn"),
        "custom_text_input": (By.CLASS_NAME, "custom-text-input"),
    }

    def click_custom_story_item_button(self, ctx: Context) -> None:
        ClickFunctions.click_element_by_name(ctx, self.locators, "add_custom_story_item")

    def enter_new_bullet_text(self, ctx: Context, text: str) -> None:
        InputFunctions.send_keys_to_element_by_name(ctx, self.locators, "custom_text_input", str)
