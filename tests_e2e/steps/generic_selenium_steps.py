"""
Generic selenium steps that will allow for all generic selenium actions.
"""
import logging
import time

from behave import given, step, use_step_matcher
from behave.runner import Context


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


@step(
    "the user goes to the page (?P<url>.*)"
)
def step_go_to_page(ctx: Context, url: str) -> None:
    ctx.driver.get(url)
