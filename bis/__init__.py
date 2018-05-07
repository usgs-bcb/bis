# BIS PACKAGE

"""

~~~~~~~~~~~~~~~~~~~~~
BIS PYTHON PACKAGE
~~~~~~~~~~~~~~~~~~~~~

A set of helper code for Biogeographic Information System projects

url : https://maps.usgs.gov/
Email : bcb@usgs.gov

Author: Core Science Analytics, Synthesis and Libraries
Core Science Systems Division, U.S. Geological Survey

Software metadata: retrieve using "bis.get_package_metadata()"

"""

import pkg_resources  # part of setuptools


# Import bis objects
from .bis import *
from .bison import *
from .gap import *
from .itis import *
from .iucn import *
from .natureserve import *
from .rrl import *
from .tess import *
from .tir import *
from .worms import *
from .sgcn import *

# provide version, PEP - three components ("major.minor.micro")
__version__ = pkg_resources.require("bis")[0].version

# metadata retrieval
def get_package_metadata():
    d = pkg_resources.get_distribution('bis')
    for i in d._get_metadata(d.PKG_INFO):
        print(i)
