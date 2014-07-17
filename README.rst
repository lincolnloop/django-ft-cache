=============================
django-ft-cache
=============================

.. image:: https://travis-ci.org/lincolnloop/django-ft-cache.png?branch=master
    :target: https://travis-ci.org/lincolnloop/django-ft-cache

A fault-tolerant pylibmc cache backend for Django

Documentation
=============

By default, a failed cache operation in Django is fatal and will raise a 500
error. In some cases, this might not be desirable behavior. This cache
backend will catch failures and log them, but not raise an exception. A
cache ``get`` that fails will appear to be a miss to the application.

Installation
------------

::

    pip install pylibmc django-ft-cache

Replace the existing pylibmc cache backend in your settings with
``'django_ft_cache.FaultTolerantPyLibMCCache'``. For example:

.. code-block:: python

    CACHES = {
        'default': {
            'BACKEND': 'django_ft_cache.FaultTolerantPyLibMCCache',
            'LOCATION': ['127.0.0.1:11211'],
        },
    }

Building Your Own
-----------------

If you are already using a custom cache backend, a mixin is provided that
should add this capability: ``django_ft_cache.FaultTolerantCacheMixin``.

