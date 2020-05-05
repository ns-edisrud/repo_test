import logging
import os
import platform
import time
from types import MethodType

from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from behave.model import Feature, Scenario, Step
from behave.runner import Context
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER as LOG
from urllib3.exceptions import ProtocolError
from xvfbwrapper import Xvfb

from generic_behave.ns_behave.common import environment_functions
from generic_behave.ns_selenium import PAGE_CLASSES

# Set up a logger
LOGGER = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------
# Behave Hooks
# -------------------------------------------------------------------------------------


def before_all(ctx: Context):
    """
    Setup run once before all end-to-end tests.

    Args:
        ctx: The behave context object.
    """
    # Read in all user data from the behave user data
    set_user_data(ctx)

    # Set all e2e behave context attributes
    set_e2e_context_attributes(ctx)

    # Setup logging, say hello, and log the framework env setup stuff
    environment_functions.setup_logging(ctx)
    log_before_all(ctx)

    # Setup Selenium
    setup_selenium(ctx)

    # Setup the page objects
    instantiate_page_objects(ctx)


def before_feature(ctx: Context, feature: Feature):
    """Setup run once before each feature.

    Args:
        ctx: The behave context object.
        feature: The behave feature object.
    """

    # Set the driver window size to mobile mode if tagged for feature
    set_mobile_mode(ctx, feature)

    # Find all scenarios w/setup and teardown tags and run them separately
    run_setup_teardown_tags(ctx, feature)

    # Make sure we auto-retry failed e2e scenarios up to the max attempts
    for scenario in feature.scenarios:
        if ctx.max_attempts:
            patch_scenario_with_autoretry(scenario, ctx.max_attempts)


def before_scenario(ctx: Context, scenario: Scenario):
    """Setup run once before each scenario.

    Args:
        ctx: The behave context object.
        scenario: The behave scenario object.
    """
    # Set the driver window size to mobile mode if tagged for scenario
    set_mobile_mode(ctx, scenario)

    # Keep track of how many times each scenario runs
    if scenario.name in ctx.scenario_run_counts:
        ctx.scenario_run_counts[scenario.name] += 1
    else:
        ctx.scenario_run_counts[scenario.name] = 1


def before_step(ctx: Context, step: Step):
    """
    Setup run once before each step.

    Args:
        ctx: The behave context object.
        step: The behave step object.
    """
    ctx.assertions_called = 0


def after_all(ctx: Context):
    """Teardown run once after all end-to-end steps.

    Args:
        ctx: The behave context object.

    """
    # Log after all
    log_after_all(ctx)
    # Tear down selenium and the webdriver
    tear_down_selenium(ctx)


def after_feature(ctx: Context, feature: Feature):
    """
    Executed once after each feature suite

    Args:
        ctx: The behave context object.
        feature: The behave feature object
    """
    # Run all the teardown scenarios that were identified in `before_feature`
    for scenario in ctx.teardown_scenarios:
        LOGGER.info(
            "Teardown scenario found in teardown list. Running it now that our feature is complete."
        )
        # Pipe the scenario into the context so we can use it downstream in child steps
        ctx.feature = feature
        ctx.scenario = scenario
        # Execute the steps of each scenario as teardown
        execute_scenario_by_steps(ctx, scenario)


def after_scenario(ctx: Context, scenario: Scenario):
    """Teardown run once after each scenario.

    Args:
        ctx: The behave context object.
        scenario: The behave scenario object.

    """
    # Check tags to make sure we shorten load timeout if present
    check_tags(ctx, scenario)

    # Screen-shot on failure of the scenario
    screenshot_on_fail(ctx, scenario)

    # # Make sure we keep some attributes on the context that are needed for the whole feature
    # save_feature_attributes(ctx)


def after_step(ctx: Context, step: Step):
    """
    Teardown run once after each step.

    Args:
        ctx: The behave context object.
        step: The behave step object.
    """
    # Only do screen-shots after step if we are in setup or teardown scenarios
    if "setup" or "teardown" in ctx.scenario.tags:
        screenshot_on_fail(ctx, step)


# -------------------------------------------------------------------------------------
# Setup Helper functions
# -------------------------------------------------------------------------------------


def set_user_data(ctx: Context) -> None:
    """Retrieve behave -userdata values, setting them on the context"""
    user_data = ctx.config.userdata
    ctx.wait_timeout = user_data.getfloat("wait_timeout", 20)
    ctx.max_attempts = user_data.getint("max_attempts", 3)
    ctx.debug_mode = user_data.getbool("debug_mode", False)
    ctx.latency = user_data.get("latency", 0)


def set_e2e_context_attributes(ctx: Context) -> None:
    """
    Setup all context attributes needed for the e2e tests

    Args:
        ctx: The behave context
    """
    ctx.mode = "e2e"
    ctx.scenario_run_counts = {}
    ctx.test_org_name = "e2e_test_org"
    ctx.test_orgs = []
    ctx.expect = MethodType(expect, ctx)
    ctx.get_page_url = MethodType(get_page_url, ctx)


def expect(ctx: Context, statement: bool):
    """Wrapper for assert to track how many assertions we run.

    Args:
        ctx: The behave context object.
        statement: Boolean expression to be asserted.

    """
    ctx.assertions_called += 1
    assert statement


def get_page_url(self) -> str:
    """Return the current page's url"""
    return self.driver.current_url


# def save_feature_attributes(ctx: Context) -> None:
#     """Save feature attributes to context so they are not deleted after the scenario"""
#     for attribute in (
#         "app_id",
#         "app_name",
#         "app_slug",
#         "dimensions_measures_map",
#         "narrative_id",
#         "narrative_name",
#         "story_title",
#         "user_id",
#         "story_config_id",
#         "bookmark_id",
#     ):
#         value = getattr(ctx, attribute, None)
#         if value is not None:
#             ctx._stack[-2][attribute] = value


# -------------------------------------------------------------------------------------
# Tag Helper Functions
# -------------------------------------------------------------------------------------


def check_tags(ctx: Context, scenario: Scenario) -> None:
    """Interpret any tags added to the scenario"""
    if "shorten_load_timeout" in scenario.tags:
        # Reset timeout back to default
        ctx.raw_data_store_client.pipeline_transform_timeout = 120
        ctx.raw_data_store_client.file_upload_timeout = 120


def run_setup_teardown_tags(ctx: Context, feature: Feature) -> None:
    """
    Finds setup and teardown tags on scenarios in feature files. If present it handles them separately than normal tags

    Args:
        ctx: The behave context
        feature: The behave feature
    """
    remaining_scenarios = []
    ctx.teardown_scenarios = []
    # Check each feature to see if we have setup or teardown tags. Else they are normal scenarios
    for scenario in feature.scenarios:
        # Pipe the feature and scenario into the context so we can use it downstream in child steps
        ctx.feature = feature
        ctx.scenario = scenario
        if "setup" in scenario.tags:
            LOGGER.info(
                "Setup scenario detected. Running it before the rest of the feature."
            )
            # Run the steps in the setup scenario as setup
            execute_scenario_by_steps(ctx, scenario)
        elif "teardown" in scenario.tags:
            LOGGER.info(
                "Teardown scenario detected. Saving it so we can run as cleanup after the rest of the feature."
            )
            ctx.teardown_scenarios.append(scenario)
        else:
            remaining_scenarios.append(scenario)
    feature.scenarios = remaining_scenarios


def execute_scenario_by_steps(ctx: Context, scenario: Scenario) -> None:
    """
    This function executes each step in a scenario with the ctx.execute steps method.
    We are doing this in place of scenario.run(ctx._runner) because that hacks the context runner
    which confuses the behave reporter and formatter causing assertion errors. This is a much smoother way
    to run steps in the before and after hook.

    Args:
        ctx: The behave context
        scenario: The behave scenario object
    """
    # Set an empty list of steps to run
    parsed_steps = []
    # For each step put the step in the parsed list
    for step in scenario.steps:
        parsed_steps.append(f"{step.keyword} {step.name}")
        # check to see if we have a table with our step. If we do make sure we put the headings
        # and rows into the parsed steps list so we execute the full step
        if step.table:
            heading_string = ""
            for heading in step.table.headings:
                heading_string += f"{heading}|"
            parsed_steps.append(f"|{heading_string}")
            for row in step.table.rows:
                row_string = "|".join(row.cells)
                parsed_steps.append(f"|{row_string}|")
    steps_string = "\n".join(parsed_steps)
    LOGGER.info(f"Steps run in setup or teardown scenario:\n{steps_string}")
    ctx.execute_steps(steps_string)


# -------------------------------------------------------------------------------------
# Selenium Helper Functions
# -------------------------------------------------------------------------------------


def setup_selenium(ctx: Context) -> None:
    """Setup the selenium browser for all e2e tests"""
    # Setup the headless browser if on linux
    if "Linux" in platform.platform():
        _setup_for_docker(ctx)

    # Set up the selenium browser
    set_up_browser(ctx)


def tear_down_selenium(ctx: Context) -> None:
    """Tear down selenium and the webdriver for which ever browser was instantiated."""
    LOGGER.debug("Tearing down selenium if the browser driver is still instantiated.")
    if ctx.driver:
        ctx.driver.quit()
        LOGGER.debug("Selenium webdriver is successfully torn down.")
        if "Linux" in platform.platform():
            ctx.vdisplay.stop()
            LOGGER.debug(
                "Virtual display from headless browser torn down successfully."
            )
    else:
        LOGGER.debug("No selenium webdriver instantiated. Nothing to tear down.")


def _setup_for_docker(ctx: Context) -> None:
    """Set up virtual display for running in headless mode.

    Args:
        ctx: The behave context object.
    """
    ctx.vdisplay = Xvfb(width=1920, height=1080)
    ctx.vdisplay.start()


def set_up_browser(ctx: Context) -> None:
    """Setup the browser we will use with selenium for testing"""
    if os.getenv("BROWSER", "Chrome") == "Firefox":
        ctx.driver = webdriver.Firefox()
    else:
        _instantiate_chromedriver(ctx)
    ctx.default_window_size = ctx.driver.get_window_size()


def instantiate_page_objects(ctx: Context) -> None:
    """Instantiate each page object, adding them to the context"""
    for cls in PAGE_CLASSES:
        setattr(ctx, cls.__name__, cls(ctx))


def _instantiate_chromedriver(ctx: Context) -> None:
    """Attempt to start the chromedriver, retrying if there are connection errors.

    Args:
        ctx: The behave context object.

    Raises:
        :py:class:`.ConnectionResetError`: If starting chromedriver fails too
            many times.
    """
    # Set the selenium logs to warning only
    LOG.setLevel(logging.WARNING)

    chrome_options = webdriver.ChromeOptions()
    # Prevent images from loading (should decrease load times)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--no-sandbox")
    # Ignore CORS errors
    chrome_options.add_argument("--disable-web-security")
    # set logging capability
    chrome_options.set_capability("loggingPrefs", {"browser": "ALL"})

    # if ctx.zap_proxy_url:
    #     chrome_options.add_argument(f"--proxy-server={ctx.zap_proxy_url}")

    chrome_options.add_argument("--window-size=1920,1080")

    # Attempt the connection... Max attempts 3
    attempts_remaining = 3
    while attempts_remaining > 0:
        try:
            LOGGER.info("Instantiating chromedriver...")
            # use the chromedriver binary loader. this forces the location on path
            chromedriver_binary.add_chromedriver_to_path()
            ctx.driver = webdriver.Chrome(chrome_options=chrome_options)
            LOGGER.debug(
                f"Chromedriver running from {chromedriver_binary.chromedriver_filename}"
            )
            LOGGER.info("Connected to chromedriver successfully!")
            break
        except (ConnectionResetError, ProtocolError):
            # one attempt used...
            attempts_remaining -= 1
            LOGGER.warning(
                "Connection was refused, will try again {} more "
                "time{}".format(
                    attempts_remaining, "" if attempts_remaining == 1 else "s"
                )
            )
            # sleep 3 seconds between attempts
            time.sleep(3)
    else:
        raise ConnectionResetError(
            "Failed connecting to chromedriver after exhausting all 3 attempts. Giving up!"
        )

    # Set the latency for the browser if not defaulted to 0
    latency = ctx.latency
    if latency != "None":
        LOGGER.debug(f"Non default latency was detected as: {latency}")
        _set_browser_latency(ctx, latency)


def _set_browser_latency(ctx: Context, latency: int) -> None:
    """Set additional latency to add to the chrome browser

    Args:
        ctx: The behave context object.
        latency: Number of milliseconds
    """
    ctx.driver.set_network_conditions(
        offline=False, latency=int(latency), download_throughput=0, upload_throughput=0
    )
    LOGGER.debug(f"Webdriver latency successfully set to {latency}")


def set_mobile_mode(ctx: Context, gherkin_object) -> None:
    """
    Set the window size for this feature to mobile mode. Default 640x1136

    Args:
        ctx: The behave context
        gherkin_object: Feature or Scenario depending on what is passed in
    """
    mobile_width = 640
    mobile_height = 1136
    if "mobile" in gherkin_object.tags:
        # default the mobile mode to 640x1136 screen size
        ctx.driver.set_window_size(mobile_width, mobile_height)
        LOGGER.info(
            f"Mobile mode detected! Running tests with browser size {mobile_width}x{mobile_height}"
        )
    else:
        # Check to see if we already set mobile mode. If we did then do not change it back to desktop for scenario
        # If we are in a new feature and we are in mobile mode with no tags... we need to reset to desktop mode.
        if ctx.driver.get_window_size()["width"] == mobile_width:
            if gherkin_object.keyword == "Feature":
                ctx.driver.set_window_size(
                    ctx.default_window_size["width"], ctx.default_window_size["height"]
                )
                LOGGER.debug("Resetting the browser mode to 'desktop'")
            elif gherkin_object.keyword == "Scenario":
                LOGGER.debug("Mobile mode was set in the feature. Continue.")
        # Check to see if we are set to non default window size or set mobile size
        elif (
            ctx.driver.get_window_size()["width"] != mobile_width
            and ctx.driver.get_window_size()["width"]
            != ctx.default_window_size["width"]
        ):
            # reset to mobile mode
            ctx.driver.set_window_size(mobile_width, mobile_height)
        # Safety... set the screen size to the default
        else:
            ctx.driver.set_window_size(
                ctx.default_window_size["width"], ctx.default_window_size["height"]
            )


def screenshot_on_fail(ctx: Context, gherkin_object) -> None:
    """
    Take a screen-shot if the scenario or step fails

    Args:
        ctx: The behave context
        gherkin_object: Feature, Scenario, or Step depending on what is passed in
    """
    screenshot_dir = os.environ.get(
        "FAILED_SCENARIOS_SCREENSHOTS_DIR",
        f"{os.getenv('TALOS_ROOT')}/tests-e2e/failed_scenarios_screenshots",
    )
    if gherkin_object.status == "failed":
        LOGGER.debug(
            f"Taking screen-shot from failed {gherkin_object.keyword}: {gherkin_object.name}"
        )
        if ctx.build_number:
            screenshot_location = os.path.join(
                screenshot_dir,
                f"{ctx.build_number}_{gherkin_object.name}_failed.png".replace(
                    " ", "_"
                ),
            )
        else:
            screenshot_location = os.path.join(
                screenshot_dir, f"{gherkin_object.name}_failed.png".replace(" ", "_")
            )
        ctx.driver.save_screenshot(screenshot_location)
        LOGGER.debug(f"Screen-shot saved at '{screenshot_location}'")


# -------------------------------------------------------------------------------------
# Logging functions
# -------------------------------------------------------------------------------------


def log_before_all(ctx: Context) -> None:
    """
    Log the before all setup for the e2e test framework

    Args:
        ctx: The behave context
    """
    LOGGER.info(
        "Welcome to the Narrative Science E2E Test Framework. Please wait while we set a few things up."
    )
    LOGGER.info(f"Behave user data read in from the behave.ini: {ctx.config.userdata}")


def log_after_all(ctx: Context) -> None:
    """
    Log the after all tear down for the e2e test framework

    Args:
        ctx: The behave context
    """
    LOGGER.info(
        "Tests have finished execution. Please wait while we clean up a few things and publish test results."
    )
