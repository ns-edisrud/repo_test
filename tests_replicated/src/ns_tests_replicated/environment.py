"""Behave framework environment configuration. This file holds all hooks and environment setup."""
# Ignoring prints in this file
# flake8: noqa
import logging

import ansicolor
from behave.model import Feature, Scenario, Step, Tag
from behave.runner import Context
from generic_behave.ns_behave.common import environment_functions
from generic_behave.ns_behave.common.common_behave_functions import CommonBehave


# Initialize a logger
LOGGER = logging.getLogger("ns_test_integration.environment")


def before_all(ctx: Context) -> None:
    """Hook that runs before all features

    Args:
        ctx: The behave context

    """
    # Setup logging
    environment_functions.setup_logging(ctx)
    log_before_all()

    # Setup environment
    setup_host(ctx)

    # Ready for testing!!
    log_before_all_complete()


def before_tag(ctx: Context, tag: Tag) -> None:
    """Hook that runs before a specific tag

    Args:
        ctx: The behave context
        tag: Behave tag

    """
    pass


def before_feature(ctx: Context, feature: Feature) -> None:
    """Hook that runs before every feature

    Args:
        ctx: The behave context
        feature: The behave feature

    """
    log_before_feature(ctx, feature)
    CommonBehave.log_context_attributes(ctx)
    # Find/do things for all scenarios w/setup and teardown tags
    environment_functions.run_setup_tags(ctx, feature)
    log_before_feature_complete(ctx, feature)


def before_scenario(ctx: Context, scenario: Scenario) -> None:
    """Hook that runs before every scenario

    Args:
        ctx: The behave context
        scenario: The behave scenario

    """
    pass


def before_step(ctx: Context, step: Step) -> None:
    """Hook that runs before every step

    Args:
        ctx: The behave context
        step: The behave step

    """
    pass


def after_all(ctx: Context) -> None:
    """Hook that runs after all features

    Args:
        ctx: The behave context

    """
    log_after_all()

    log_after_all_complete()


def after_tag(ctx: Context, tag: Tag) -> None:
    """Hook that runs after a specific tag

    Args:
        ctx: The behave context
        tag: the behave tag

    """
    pass


def after_feature(ctx: Context, feature: Feature) -> None:
    """Hook that runs after every feature

    Args:
        ctx: The behave context
        feature: The behave feature

    """
    log_after_feature(ctx, feature)
    # Run any scenarios denoted by @teardown tags
    environment_functions.run_teardown_tags(ctx, feature)
    log_after_feature_complete(ctx, feature)


def after_scenario(ctx: Context, scenario: Scenario) -> None:
    """Hook that runs after every scenario

    Args:
        ctx: The behave context
        scenario: The behave scenario

    """
    pass


def after_step(ctx: Context, step: Step) -> None:
    """Hook that runs after every step

    Args:
        ctx: The behave context
        step: The behave step

    """
    pass


# -------------------------------------------------------------------------------------
# Logging functions
# -------------------------------------------------------------------------------------


def log_before_all() -> None:
    """Log the before all setup for the integration test framework"""
    LOGGER.info(
        "Welcome to the Narrative Science Integration Test Framework. Please wait while we set a few things up."
    )


def log_before_all_complete() -> None:
    """Log the before all complete"""
    LOGGER.info("Framework and environment setup is complete! Starting tests...")


def log_before_feature(ctx: Context, feature: Feature) -> None:
    """Log the before feature setup"""
    if ctx.config.logging_level == 10:
        print(
            ansicolor.magenta(f"---------- BEFORE FEATURE: {feature.name} ----------")
        )


def log_before_feature_complete(ctx: Context, feature: Feature) -> None:
    """Log the before feature setup"""
    if ctx.config.logging_level == 10:
        print(
            ansicolor.magenta(
                f"---------- BEFORE FEATURE COMPLETE: {feature.name} ----------\n"
            )
        )


def log_after_feature(ctx: Context, feature: Feature) -> None:
    """Log the before feature setup"""
    if ctx.config.logging_level == 10:
        print(
            ansicolor.magenta(f"\n---------- AFTER FEATURE: {feature.name} ----------")
        )


def log_after_feature_complete(ctx: Context, feature: Feature) -> None:
    """Log the before feature setup"""
    if ctx.config.logging_level == 10:
        print(
            ansicolor.magenta(
                f"---------- AFTER FEATURE COMPLETE: {feature.name} ----------"
            )
        )


def log_after_all() -> None:
    """Log the after all tear down"""
    LOGGER.info(
        "Integration tests have finished execution. "
        "Please wait while we clean up a few things and publish test results."
    )


def log_after_all_complete() -> None:
    """Log the after all teardown complete"""
    LOGGER.info(
        "Clean up is complete. Test results published. "
        "Shutting down the Narrative Science Integration Test Framework. Goodbye!!"
    )


def setup_host(ctx: Context) -> None:
    ctx.gateway_base_url = ctx.config.userdata['environment']
