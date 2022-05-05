import os
from setuptools import setup, find_packages

current_dir = os.path.dirname(__file__)


# Can't import module here, because dependencies might not be available, so we
# parse it manually.
def _get_version():
    with open(os.path.join(current_dir, "metering/version.py")) as f:
        for line in f.readlines():
            if line.startswith("VERSION"):
                start = line.find('"') + 1
                end = line.rfind('"')
                return line[start:end]


version = _get_version()


with open(os.path.join(current_dir, "README.md")) as f:
    long_description = f.read()

install_requires = [
    "requests",  # https://docs.python-requests.org/
    "backoff",  # https://pypi.org/project/backoff/
]

extras_require = {
    "s3": [
        "boto3",  # https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    ],
}

packages = [p for p in find_packages() if "tests" not in p]


setup(
    name="amberflo-metering-python",
    version=version,
    url="https://github.com/amberflo/metering-python",
    author="Amberflo",
    author_email="friends@amberflo.com",
    maintainer="Amberflo.io",
    maintainer_email="friends@amberflo.com",
    packages=packages,
    license="MIT License",
    install_requires=install_requires,
    extras_require=extras_require,
    description="Integrate Amberflo into any Python 3 application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
