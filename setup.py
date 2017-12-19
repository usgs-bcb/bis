# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


# Utility function to read the README file.
def read(fname):
    return open(path.join(path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name='bis',

# PEP - version as three components ("major.minor.micro")
    version='0.0.2',

    description='A set of helper code for Biogeographic Information System projects',
    long_description=read('README.rst'),

    url='https://maps.usgs.gov/',

    author='USGS CSASL BCB',
    author_email='bcb@usgs.gov',

    license='None',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: CC0',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='biogeography',

    packages=['bis'],
)
