===========
workedon
===========


.. image:: https://img.shields.io/pypi/v/workedon.svg
        :target: https://pypi.python.org/pypi/workedon

.. image:: https://img.shields.io/pypi/pyversions/workedon.svg?logo=python&logoColor=white
        :target: https://pypi.org/project/workedon/
        :alt: Python versions

.. image:: https://github.com/viseshrp/workedon/workflows/Test/badge.svg
        :target: https://github.com/viseshrp/workedon/actions?query=workflow%3ATest
        :alt: Tests status

.. image:: https://codecov.io/gh/viseshrp/workedon/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/viseshrp/workedon
        :alt: Coverage

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://github.com/viseshrp/workedon/blob/develop/LICENSE
        :alt: License

.. image:: https://pepy.tech/badge/workedon
        :target: https://pepy.tech/project/workedon
        :alt: Downloads

| CLI utility for daily work logging.


.. image:: demo.gif
   :alt: demo
   :align: center


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
* dateparser_, for an amazing date parser. This project would not be possible without it.
* jrnl_, fck_ and sqlite-utils_ for some inspiration.

.. _Click: https://click.palletsprojects.com
.. _dateparser: https://github.com/scrapinghub/dateparser
.. _jrnl: https://github.com/jrnl-org/jrnl
.. _fck: https://github.com/nvbn/thefuck
.. _sqlite-utils: https://github.com/simonw/sqlite-utils/
