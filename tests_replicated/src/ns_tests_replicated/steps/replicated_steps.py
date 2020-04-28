"""
Step definitions for Replicated tests
"""
import logging
import requests
import boto3
import json

from behave import given, then, when, use_step_matcher
from behave.runner import Context
from generic_behave.test_utils.behave.src.ns_behave.step_library.generic_behave_steps import generic_assert_steps

# Enable the regex step matcher for behave in this class
use_step_matcher("re")
# Set up a logger
LOGGER = logging.getLogger(__name__)


@given("a version request is sent to the replicated test stack")
def request_version(ctx: Context):
    LOGGER.debug('Attempting to send a version request to the replicated test stack')
    ctx.response = requests.Session().request(
        method="get", url=ctx.gateway_base_url, verify=False
    )
    response = ctx.response.text
    LOGGER.debug(f"Successfully sent a version request to the replicated test stack with response: {response}")


@then('the viz-server version is "(?P<version>.*)"')
def validate_version(ctx: Context, version: str):
    generic_assert_steps.step_assert_rest_response_value(ctx, "version", None, version)


@given('the test data is retrieved from S3')
def retrieve_s3_payload(ctx: Context):
    s3 = boto3.client('s3')
    payload = s3.get_object(Bucket='s3-ns-viz', Key='datasets/regression-datasets/Scatterplot/v2_scatterplot_2M.json')
    ctx.request_data = json.loads(payload["Body"].read().decode())
    LOGGER.debug(ctx.request_data)


@when('a story request is sent to (?P<url>.*)')
def request_story(ctx: Context, url: str):
    LOGGER.debug(f'Attempting to send a story request to {url}')
    ctx.response = requests.Session().request(
        method="post", url=ctx.gateway_base_url + url, verify=False, json=ctx.request_data
    )
    response = ctx.response.text
    LOGGER.debug(f"Successfully sent a story request with response: {response}")


@given('the viz extension (?P<extension>.*) is polled')
def poll_extension(ctx: Context, extension: str):
    LOGGER.debug(f'Attempting poll viz extension: {extension}')
    ctx.response = requests.Session().request(
        method="get", url='{}v1/extensions/{}/static/main.js'.format(ctx.gateway_base_url, extension), verify=False
    )
    LOGGER.debug(f'Successfully polled viz extension: {extension}')
