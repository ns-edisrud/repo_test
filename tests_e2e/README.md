# End-to-End Tests

## Directory Structure

* `datasets/` - Data files used for e2e tests
* `failed_scenario_screenshots/` - Screenshots of failed test runs will be placed here.
* `features/` -  Feature files written using Gherkin syntax.
* `pages/` - Python page object classes containing selectors and functions for interacting with UI elements.
* `steps/` - Python files with e2e step definitions.
* `utils/` - Test utility files.
* `README.md` - This readme.
* `behave.ini` - Configuration file for behave e2e tests.
* `environment.py` - Behave module defining setup and teardown of the test environment.
* `lint_e2e.py` - Custom lint script that runs during pull requests

## Running tests with Docker

The Talos CI pipeline uses Docker images to run the e2e tests. Running the tests locally inside of a `runtime-dev` Docker image will most closely match the behavior of the tests in the pipeline. This will not display the browser that the tests run in, however, since the tests use the image's headless browser which can't be displayed on your local machine.

### Set environment variables

The following environment variables are used by the selenium tests:

```bash
TALOS_BASE_URL
TALOS_GATEWAY_HOST
TALOS_TEST_EMAIL
TALOS_TEST_PASSWORD
```

Note that the test setup script will automatically try to find the right UI and Gateway hosts by attempting to connect to the service's appropriate docker-compose hostname alias or localhost. Unless you are running a bespoke Talos stack, you may as well not set the `TALOS_BASE_URL` and `TALOS_GATEWAY_HOST` variables.

With that being said, if you want to set specific hosts, and are running the tests locally using the docker-compose method described in this section:

* `TALOS_BASE_URL` should be set to `http://ui:3000`
* `TALOS_GATEWAY_HOST` should be set to `http://gateway:3100`

### Run the tests

The tests expect a running instance of Talos to run against (e.g. run `startTalos` first). Once Talos is running (you should be able to see the UI in your browser), you can source the `start-dev.sh` script then run the tests with:

```bash
runBehaveE2E
```

This will spin up a container based on the runtime image, run the tests, show the output in the terminal, and remove the container.

### Run tests in firefox

Build the firefox container:

```bash
docker build -f - < $DOCKER_ROOT/images/talos/test/e2e/firefox/Dockerfile -t \
talos/selenium-firefox $TALOS_ROOT/tests-e2e
```

Run tests:

```bash
docker run --env-file $DOCKER_ROOT/images/talos/test/e2e/e2e_env --net="host" \
-v $TALOS_ROOT:/apps/talos talos/selenium-firefox behave
```

## Running tests locally (outside Docker so you can see the browser)

Install the following on your machine:

* [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
* [Google Chrome](https://www.google.com/chrome/browser/desktop/index.html)
* [pipenv](https://pypi.python.org/pypi/pipenv)

There are several environment variables that need to be overwritten in your local environment, which you can add to your bash profile without affecting the values used in your Docker images:

```bash
export TALOS_BASE_URL=http://localhost:3000
export TALOS_GATEWAY_HOST=http://localhost:3100
export CONFIG_DB_USERNAME=nssvc
export CONFIG_DB_HOST=localhost
export CONFIG_DB_PORT=5432
export CONFIG_DB_NAME=dev_talos
export RAW_DATA_STORE_USERNAME=nssvc
export RAW_DATA_STORE_HOST=localhost
export RAW_DATA_STORE_PORT=5432
export RAW_DATA_STORE_NAME=raw_data_store
export DATA_CACHE_USERNAME=nssvc
export DATA_CACHE_HOST=localhost
export DATA_CACHE_PORT=5432
export DATA_CACHE_NAME=data_warehouse
export TALOS_RAW_WAY_STATION_DB_CONNECTION_STRING='postgresql://nssvc@localhost:5432/raw_data_store'
export TALOS_CACHE_CONNECTION_STRING='redis://localhost:6379'
export ML_ROOT=$TALOS_ROOT/ml/dev
export ONTOLOGY_SNAPSHOT_PATH=$TALOS_ROOT/ontology_snapshots
export TALOS_TEST_EMAIL="test@narrativescience.com"
export TALOS_TEST_PASSWORD="replace me"
```

Create a sym link from /apps to your talos folder:
```bash
sudo mkdir /apps
sudo ln -s <talos_folder_location> /apps
```

Install Talos dependencies inside a virtualenv:

Make sure you have pipenv installed first:
```bash
brew install pipenv
```

NOTE: make sure you are doing this in a 3.6 environment.  Currently talos is not supported on 3.7

```bash
cd $TALOS_ROOT
pipenv shell
# The Pipfile specifies absolute paths that assume the install is happening in
# a docker environment, so this overwrites the paths to match your local
# environment while installing
find Pipfile* -type f -exec sed -i '' "s~\/apps\/talos~${TALOS_ROOT}~g" {} \; && pipenv install --dev --system && git checkout Pipfile.lock && git checkout Pipfile
cd tests-e2e
behave
```

If the `behave` command can't be found, add `--python < python version >` to the end of the `pipenv install` command in the above command, e.g. `pipenv install --dev --system --python 3.6.1`

You may get an error that says `'chromedriver' executable needs to be in PATH.` If so, follow the link above to install Chromedriver, unzip it inside the Downloads folder, then run the following:

```bash
mv ~/Downloads/chromedriver /usr/local/bin
```

After this, you should be able to run `behave` again.

## Test Logging
The test framework and all tests support logging with behave.logging. This is setup to run with LEVEL=INFO by default.

To enable debug mode you need to modify set debug_mode flag to True. This can be done in the behave.ini or by passing a behave user data param from the cmd line.

ex:
```bash
behave -D debug_mode=True
```

## E2E Test Tags

* `@new` - New tests run in the pull request job and not in the deploy job. Once a test has demonstrated sufficient stability, the tag is removed and the test only runs in the deploy job.
* `@smoke` - Smoke tests run in the pull request job and the deploy job.
* `@skip` - Tests can be skipped on a short term basis, but only if there is a corresponding jira ticket number next to the skip.

## Writing Tests

Please review the [Selenium Best Practices and Conventions](https://confluence.n-s.us/pages/worddav/preview.action?fileName=Selenium+Best+Practices+and+Conventions.docx&pageId=2135352) doc for more information on writing effective Selenium tests.

For more information on writing Behave tests, see the [integration test README](https://github.com/NarrativeScience/talos/tree/master/tests-integration#writing-a-test).

**NOTE:** Remember that all tests and steps that are written should have debug logs baked into them for easier debugging when necessary.

## Adding Latency to Tests

Running tests with additional latency can help identify flaky tests. If a test passes with 1 or 2 seconds of additional latency, then the test will be more robust when running in slower machines or during network latency spikes. You can run the tests with latency by setting `latency`, e.g.:

```bash
behave -D latency=1000 # 1000 ms of latency
behave -D latency=jenkins # Latency will approximate jenkins latency
behave -D latency=2xjenkins # Latency will be about double jenkins latency
behave -D latency=Nxjenkins # Latency will be about N times jenkins latency
```

## Linting Tests

In addition to the flake8 linter, a custom linting script runs against the e2e
test files as part the pull request job. It checks for unused and duplicate
page object locators. The script will run automatically during the pull request
job, but can also be run locally from inside a docker container, e.g.:

```bash
attachContainer runtime
python tests-e2e/lint_e2e.py
```
