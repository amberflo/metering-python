
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import metering-python module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'metering'))
from version import VERSION

long_description = '''
Amberflo is the simplest way to integrate metering into your application.

This is the official python client that wraps the Amberflo REST API (https://amberflo.io).

Samples:

        # dedup is happening on a full record
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions) 
        # addint a timestamp
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), \
            dimensions=dimensions,timestamp=str(int(round(time.time() * 1000)))) 
        # adding unique id
        metering.meter(options.tenant, options.meter_name,int(options.meter_value), dimensions=dimensions_with_unique_id) 
        

Documentation and more details at https://github.com/amberflo/metering-python
'''

install_requires = [
    "requests>=2.7,<3.0",
    "six>=1.5",
    "monotonic>=1.5",
    "backoff==1.10.0",
    "python-dateutil>2.1"
]

tests_require = [
    "mock==2.0.0",
    "pylint==1.9.3",
    "flake8==3.7.9",
    "coverage==4.5.4"
]

setup(
    name='amberflo-metering-python',
    version=VERSION,
    url='https://github.com/amberflo/metering-python',
    author='Segment',
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
    description='The hassle-free way to integrate amberflo into any python application.',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
