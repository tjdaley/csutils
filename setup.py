"""
setup.py - For Pypi installer.

Update package with the following commands:

$ python setup.py sdist bdist_wheel
$ twine check dist/*
$ twine upload --config-file .pypirc --repository csutils dist/*
"""
import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.4'
PACKAGE_NAME = 'csutils'
AUTHOR = 'Thomas J. Daley, J.D.'
AUTHOR_EMAIL = 'tom@powerdaley.com'
URL = 'https://github.com/tjdaley/csutils'

LICENSE = 'BSD-3-Clause License'
DESCRIPTION = 'Child Support Utilities'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'python_dateutil'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )