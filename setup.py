
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import metering-python module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'metering'))
from metering.version import VERSION

long_description = '''
Amberflo is the simplest way to integrate metering into your application.

This is the official python client that wraps the Amberflo REST API (https://amberflo.io).

Samples:

# dedup is happening on a full record

metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=current_time, \
    customer_id=options.customer_id)

# adding dimensions

metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=current_time, \
    customer_id=options.customer_id, \
    dimensions=dimensions)

# adding unique id

metering.meter(options.meter_api_name, \
    int(options.meter_value), \
    meter_time_in_millis=current_time, \
    customer_id=options.customer_id, \
    dimensions=dimensions, \
    unique_id = uuid1())

Documentation and more details at https://github.com/amberflo/metering-python
'''

install_requires = [
    "requests>=2.20,<3.0", # https://requests.readthedocs.io/en/latest/community/updates/#release-history
    "backoff==1.10.0", # https://pypi.org/project/backoff/
    "python-dateutil>=2.5", # https://dateutil.readthedocs.io/en/stable/changelog.html
    "boto3>=1.18.47"
]


tests_require = [
    "mock==3.0.5",
    "pylint==1.9.5", # http://pylint.pycqa.org/en/latest/whatsnew/2.0.html
    "flake8==3.7.9", # https://pypi.org/project/flake8/#history
    "coverage==4.5.4" # https://mock.readthedocs.io/en/latest/changelog.html
]

setup(
    name='amberflo-metering-python',
    version=VERSION,
    url='https://github.com/amberflo/metering-python',
    author='Amberflo',
    author_email='friends@amberflo.com',
    maintainer='Amberflo.io',
    maintainer_email='friends@amberflo.com',
    test_suite='metering.test.all',
    packages=['metering', 'metering.test'],
    license='MIT License',
    install_requires=install_requires,
    extras_require={
        'test': tests_require
    },
    description='Integrate amberflo into any python application.',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
