===========
workedon
===========


.. image:: https://img.shields.io/pypi/v/workedon.svg
        :target: https://pypi.python.org/pypi/workedon

.. image:: https://pepy.tech/badge/workedon
        :target: https://pepy.tech/project/workedon
        :alt: Downloads


CLI tool to get package info from PyPI and/or manipulate requirements.


Installation
------------

.. code-block:: bash

    $ pip install -U workedon


Requirements
------------

Python 3.7+


Features
--------

* Save by date or fetch work saved by date.

    Examples:

    .. code-block:: bash

        # Saving work:
        $ workedon studying for the SAT @ June 2010
        $ workedon pissing my wife off @ 2pm yesterday
        $ workedon painting the garage

        # Fetching work:
        $ workedon what
        $ workedon what --from "2pm yesterday" --to "9am today"
        $ workedon what --today
        $ workedon what --past-month

See all options with:

.. code-block:: bash

    $ workedon --help
    $ workedon what --help

Credits
-------
* Click_, for making writing CLI tools a complete pleasure.
* dateparser_, for an amazing date parser.
* jrnl_ and `fck`_ for some inspiration.

.. _Click: https://click.palletsprojects.com
.. _dateparser: https://github.com/scrapinghub/dateparser
.. _jrnl: https://github.com/jrnl-org/jrnl
.. _fck: https://github.com/nvbn/thefuck