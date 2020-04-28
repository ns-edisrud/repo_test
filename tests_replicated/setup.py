import os

import setuptools

setuptools.setup(
    name='ns_tests_replicated',
    version=os.environ.get("BUILD_VERSION", "0.0.0.dev-1"),
    install_requires=open("requirements.txt").readlines(),
)
