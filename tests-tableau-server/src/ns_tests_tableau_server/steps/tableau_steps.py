"""
Generic selenium steps that will allow for all generic selenium actions.
"""
import logging
import time

from behave import given, step, then, use_step_matcher
from behave.runner import Context

from generic_behave.ns_selenium.selenium_functions.general_functions import GeneralFunctions
from generic_behave.ns_selenium.selenium_functions.assert_functions import AssertFunctions

# Initialize a logger
LOGGER = logging.getLogger(__name__)

# Enable the regex step matcher for behave in this class
use_step_matcher("re")


@step("I wait (?P<wait_time>\d+) second(?:s|)?")
def step_wait(ctx: Context, wait_time: int) -> None:
    """
    This step will be used for debugging purposes ONLY!!! It will allow for a sleep to see the selenium actions

    Args:
        ctx: The behave context.
        wait_time: The time in seconds we will wail.
    """
    LOGGER.debug(f"Sleeping for {wait_time} second(s)")
    time.sleep(int(wait_time))


@given("the browser size of (?P<width>\d+)x(?P<height>\d+)")
def step_set_browser_size(ctx: Context, width: int, height: int) -> None:
    """
    This step will set the browser size to a custom dimension for width and height.

    Args:
        ctx: The behave context.
        width: The width to set.
        height: The height to set.
    """
    LOGGER.debug(f"Attempting to set the browser size to {width}x{height}")
    ctx.driver.set_window_size(width, height)
    LOGGER.debug(f"Browser size successfully set to {width}x{height}")


@step("the user goes to the page (?P<url>.*)"
      )
def step_go_to_page(ctx: Context, url: str) -> None:
    ctx.driver.get(url)


@step("the user logs in")
def step_logi_in(ctx: Context) -> None:
    ctx.SigninPage.log_in(ctx)


@step("the user clicks the (?P<tab_name>edit) tab")
def step_click_tableau_tab(ctx: Context, tab_name: str) -> None:
    ctx.WorkbookPage.click_tab(ctx, f'{tab_name}_tab')


@step("the user opens the edit story modal")
def step_open_story_modal(ctx: Context) -> None:
    ctx.WorkbookEditPage.click_edit_story(ctx)


@then('the user is on the (?P<url_link>edit story) page')
def step_verify_external_page(ctx: Context, url_link: str) -> None:
    """Step to verify that a user is on the correct page from the sidebar link

    Args:
        ctx: The behave context object
        url_link: The name of the URL link the user wants to click on

    Returns:
        None

    """
    LOGGER.debug(f"Attemping to verify the user is on the {url_link} page.")
    assert AssertFunctions.validate_url_contains(
        ctx,
        "https://stg-viz-saas-extensions.n-s.us/v1/extensions/tableau-settings/0.0/static/index.html?user_key"), (
        f"Expected url to contain: {url_link} "
        f"but we found: {ctx.driver.current_url}"
    )
    LOGGER.debug(f"Successfully verified the user is on the {url_link} page.")


@step('the user clicks on the add custom story item button')
def step_click_add_custom_story_button(ctx: Context) -> None:
    ctx.EditStoryModal.click_custom_story_item_button(ctx)


@step('the user enters "(?P<input_text>.*)" into the custom content box')
def step_enter_text_into_custom_content_box(ctx: Context, input_text: str) -> None:
    LOGGER.debug(input_text)
    ctx.EditStoryModal.enter_new_bullet_text(ctx, input_text)
