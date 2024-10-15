.. _developers:

==========
Developers
==========

Reports
-------
.. code-block:: sh
    :caption: Code coverage

    coverage run -m pytest -q
    coverage report -m
    coverage html

Open `coverage.py report <../../../coverage/index.html>`_

.. code-block:: sh
    :caption: Type checking

    mypy

Open `mypy report <../../../mypy/index.html>`_

Delivery
--------
.. toctree::
    :maxdepth: 2

    deploy_procedure
