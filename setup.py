import pathlib
from setuptools import find_packages, setup

from docly import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
name='docly',
description="Generate docstrings for your python functions. Automatically!",
long_description=README,
long_description_content_type="text/markdown",
url="https://github.com/autosoft-dev/docly",
author="CodistAI",
author_email="shubhadeep@codist-ai.com",
include_package_data=True,
license="MIT",
classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
],
version=__version__,
packages=find_packages(exclude=("tests",)),
install_requires=["tqdm", "requests", "torch", 
                  "pyfiglet", "rich", "dpu-utils", "numpy", 
                  "nltk", "transformers==2.5.0", "tree_hugger",
                  "halo", "invoke",
                  ],
extras_require={
        "jupyter": ["jupytext"]
},
entry_points = {
    'console_scripts': ['docly-gen=docly.cli.docly_gen:main',
                        'docly-restore=docly.cli.docly_restore:main'],
},
)
