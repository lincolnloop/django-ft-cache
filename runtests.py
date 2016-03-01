import sys

try:
    from django.conf import settings

    settings.configure(
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
            }
        },
        LOGGING={
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers': {
                'django_ft_cache': {
                    'handlers': [], # for debugging use ['console'],
                },
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
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")


def run_tests(*test_args):

    # Run tests
    test_runner = DiscoverRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
