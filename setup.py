import codecs
import os
import re
from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='phoenix_letter',
    version=find_version("src", "phoenix_letter", "version.py"),
    url='https://github.com/renanvieira/dlq-mover',
    license='MIT',
    author='Renan Vieira',
    author_email='me@renanvieira.net',
    package_dir={'phoenix_letter': 'src/phoenix_letter'},
    packages=find_packages('src'),
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    description='Lib to move messages from AWS SQS Queue to another',
    python_requires='>=3.5',
    zip_safe=False,
    entry_points={
        'console_scripts': ['phoenix_letter=phoenix_letter.main:main']
    }
)
