# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bis',

    version='0.1',

    description='A set of helper code for Biogeographic Information System projects',
    long_description=long_description,

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

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    py_modules=["tir"],

)
