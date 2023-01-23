"""The setup script."""
import os

from setuptools import find_packages, setup

REQUIREMENTS = [
    "click>=8.1.1",
    "colorama>=0.4.4",
    "dateparser>=1.1.4",
    "tzlocal>=4.0",
    "backports.zoneinfo>=0.2.1;python_version < '3.9'",
    "click-default-group>=1.2.2",
    "peewee>=3.15.2",
    "platformdirs>=2.6.0",
]

curr_dir = os.path.abspath(os.path.dirname(__file__))


def get_file_text(file_name):
    with open(os.path.join(curr_dir, file_name), encoding="utf-8") as in_file:
        return in_file.read()


_init = {}
_init_file = os.path.join(curr_dir, "workedon", "__init__.py")
with open(_init_file) as fp:
    exec(fp.read(), _init)
name = _init["__name__"]
version = _init["__version__"]
author = _init["__author__"]
email = _init["__email__"]

setup(
    name=name,
    version=version,
    description="CLI tool for daily work logging.",
    long_description=get_file_text("README.rst") + "\n\n" + get_file_text("CHANGELOG.rst"),
    long_description_content_type="text/x-rst",
    author=author,
    author_email=email,
    maintainer=author,
    maintainer_email=email,
    license="MIT license",
    packages=find_packages(include=["workedon"], exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/viseshrp/workedon",
    project_urls={
        "Documentation": "https://github.com/viseshrp/workedon",
        "Changelog": "https://github.com/viseshrp/workedon/blob/main/CHANGELOG.rst",
        "Bug Tracker": "https://github.com/viseshrp/workedon/issues",
        "Source Code": "https://github.com/viseshrp/workedon",
    },
    python_requires=">=3.7",
    keywords="workedon work worklog log journal",
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "workedon=workedon.__main__:main",
        ],
    },
)
