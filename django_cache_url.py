# -*- coding: utf-8 -*-

import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


# Register cache schemes in URLs.
urlparse.uses_netloc.append('db')
urlparse.uses_netloc.append('dummy')
urlparse.uses_netloc.append('file')
urlparse.uses_netloc.append('locmem')
urlparse.uses_netloc.append('memcached')
urlparse.uses_netloc.append('djangopylibmc')
urlparse.uses_netloc.append('pymemcached')
urlparse.uses_netloc.append('redis')
urlparse.uses_netloc.append('hiredis')

DEFAULT_ENV = 'CACHE_URL'

CACHE_TYPES = {
    'db': 'django.core.cache.backends.db.DatabaseCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'file': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache',
    'memcached': 'django.core.cache.backends.memcached.PyLibMCCache',
    'djangopylibmc': 'django_pylibmc.memcached.PyLibMCCache',
    'pymemcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'redis': 'redis_cache.cache.RedisCache',
    'hiredis': 'redis_cache.cache.RedisCache',
}


def config(env=DEFAULT_ENV, default='locmem://'):
    """Returns configured CACHES dictionary from CACHE_URL"""
    config = {}

    s = os.environ.get(env, default)

    if s:
        config = parse(s)

    return config


def parse(url):
    """Parses a cache URL."""
    config = {}

    url = urlparse.urlparse(url)
    # Update with environment configuration.
    config['BACKEND'] = CACHE_TYPES[url.scheme]
    if url.scheme == 'file':
        config['LOCATION'] = url.path
        return config
    elif url.scheme in ('redis', 'hiredis'):
        path = filter(None, url.path.split('/'))
        config['LOCATION'] = ':'.join((url.netloc, path[0]))
        config['KEY_PREFIX'] = '/'.join(path[1:])
        if url.scheme == 'hiredis':
            config['OPTIONS'] = {
                'PARSER_CLASS': 'redis.connection.HiredisParser'}
    else:
        netloc_list = url.netloc.split(',')
        if len(netloc_list) > 1:
            config['LOCATION'] = netloc_list
        else:
            config['LOCATION'] = url.netloc
        config['KEY_PREFIX'] = url.path[1:]

    return config
