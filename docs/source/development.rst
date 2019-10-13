.. _development:

Development and Testing
=======================

Installing for Development
--------------------------

1. Clone the git repo.
2. ``virtualenv --python=python3.6 .``
3. ``python setup.py develop``
4. ``pip install tox``
5. Make changes as necessary. Run tests with ``tox``.

Testing
-------

Testing is done via `tox <https://tox.readthedocs.io/en/latest/>`_ and `pytest <https://docs.pytest.org/en/latest/>`_. ``pip install tox`` then ``tox`` to run tests.

The package itself uses the wonderful :ref:`requests package <requests:introduction>` as a HTTP(S) client. Tests use the `betamax <http://betamax.readthedocs.io/en/latest/index.html>`_ package to record and replay HTTP(S) requests and responses. When adding a new test using betamax, set ``JIVEAPI_TEST_MODE=--record`` in your environment to capture and record new requests - otherwise, outgoing HTTP requests will be blocked. To re-record a test, delete the current capture from ``tests/fixtures/cassettes``. Before committing test data, please inspect it and be sure that no sensitive information is included. To print all base64 bodies from a specific betamax "cassette", you can use ``jiveapi/tests/fixtures/showcassette.py``.
