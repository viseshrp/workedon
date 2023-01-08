"""The setup script."""
import os
from io import open

from setuptools import setup, find_packages

REQUIREMENTS = [
    "click==8.1.3",
    "dateparser==1.1.5",
    "tzlocal==4.2",
    "backports.zoneinfo==0.2.1;python_version < '3.9'",
    "click-default-group==1.2.2",
    "peewee==3.15.4",
    "platformdirs==2.6.2",
]

curr_dir = os.path.abspath(os.path.dirname(__file__))


def get_file_text(file_name):
    with open(os.path.join(curr_dir, file_name), "r", encoding="utf-8") as in_file:
        return in_file.read()


_version = {}
_version_file = os.path.join(curr_dir, "workedon", "__init__.py")
with open(_version_file) as fp:
    exec(fp.read(), _version)
version = _version["__version__"]

setup(
    name="workedon",
    version=version,
    description="CLI tool for daily work logging.",
    long_description=get_file_text("README.rst")
    + "\n\n"
    + get_file_text("CHANGELOG.rst"),
    long_description_content_type="text/x-rst",
    author="Visesh Prasad",
    author_email="visesh@live.com",
    maintainer="Visesh Prasad",
    maintainer_email="visesh@live.com",
    license="MIT license",
    packages=find_packages(include=["workedon"]),
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
    test_suite="tests",
    tests_require=[
        "pytest",
    ],
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "workedon=workedon.__main__:main",
        ],
    },
)
