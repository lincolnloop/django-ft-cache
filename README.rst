=============================
django-ft-cache
=============================

.. image:: https://travis-ci.org/lincolnloop/django-ft-cache.png?branch=master
    :target: https://travis-ci.org/lincolnloop/django-ft-cache

Pylibmc cache backends for Django with for fault tolerance and cache stampede
mitigation. Supported against stable Django versions 1.8, 1.10, and 1.11 and
Python 2/3, but _should_ be compatible back to Django 1.5.

Documentation
=============

This offers two improvements over Django's default memcached module. They can
be used independently or together:

* ``django_ft_cache.FaultTolerantPyLibMCCache``
    **Treat cache failures as a cache miss.** By default, a failed cache
    operation in Django is fatal and will raise a 500 error. In some cases,
    this might not be desirable behavior. This cache backend will catch failures
    and log them, but not raise an exception. A cache ``get`` that fails will
    appear to be a miss to the application.
* ``django.ft_cache.PyLibMCMintCache``
    **Cache stampede mitigation.**
    `Cache stampedes <https://en.wikipedia.org/wiki/Cache_stampede>`__ happen
    when a cache key expires and multiple clients try to recompute the cache
    key simultaneously. This uses a technique where stale values are put back
    into the cache while one client recomputes the new value. This
    implementation was adapted from
    `Django Snippet #155 (aka MintCache) <https://www.djangosnippets.org/snippets/155/>`__
    and `django-newcache <https://github.com/ericflo/django-newcache>`__.
* ``django_ft_cache.FaultTolerantPyLibMCMintCache``
    **A combination of both modules above.**

Installation
------------

::

    pip install pylibmc django-ft-cache

Replace the existing pylibmc cache backend in your settings with one of the
caches provided. For example:

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
can add this capability: ``django_ft_cache.FaultTolerantCacheMixin``. The mixins
have only been tested against
``django.core.cache.backends.memcached.PyLibMCCache`` so do your own testing to
make sure they work with your backend.

