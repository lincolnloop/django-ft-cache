import logging
import sys

try:
    from django.conf import settings

    settings.configure(
        CACHE_HERD_TIMEOUT=1,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        CACHES={
            'default': {
                'BACKEND': 'django_ft_cache.FaultTolerantPyLibMCCache',
                'LOCATION': ['127.0.0.1:11211'],
            },
            'faulty': {
                'BACKEND': 'django_ft_cache.FaultTolerantPyLibMCCache',
                'LOCATION': ['127.0.0.1:999999'],
            },
            'mint': {
                'BACKEND': 'django_ft_cache.PyLibMCMintCache',
                'LOCATION': ['127.0.0.1:11211'],
            },
            'ft-mint': {
                'BACKEND': 'django_ft_cache.FaultTolerantPyLibMCMintCache',
                'LOCATION': ['127.0.0.1:11211'],
            },
            'ft-mint-faulty': {
                'BACKEND': 'django_ft_cache.FaultTolerantPyLibMCMintCache',
                'LOCATION': ['127.0.0.1:999999'],
            },
        }
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()
    from django.test.runner import DiscoverRunner
except ImportError:
    raise ImportError("To fix this error, run: pip install Django")


def run_tests(*test_args):

    # Disable logging for tests
    logging.disable(logging.ERROR)

    # Run tests
    test_runner = DiscoverRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
