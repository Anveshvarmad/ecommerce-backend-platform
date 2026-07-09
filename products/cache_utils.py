import hashlib

from django.core.cache import cache


CATALOG_CACHE_PREFIX = "catalog"
CATALOG_CACHE_TIMEOUT = 60 * 5


def build_catalog_cache_key(request, namespace):
    raw_key = f"{namespace}:{request.get_full_path()}"
    hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"{CATALOG_CACHE_PREFIX}:{namespace}:{hashed}"


def get_cached_catalog_response(cache_key):
    return cache.get(cache_key)


def set_cached_catalog_response(cache_key, data, timeout=CATALOG_CACHE_TIMEOUT):
    cache.set(cache_key, data, timeout=timeout)


def invalidate_catalog_cache():
    try:
        cache.delete_pattern(f"{CATALOG_CACHE_PREFIX}:*")
    except AttributeError:
        cache.clear()
