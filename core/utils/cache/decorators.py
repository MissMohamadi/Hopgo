import os
from django.views.decorators.cache import cache_page
from django.utils.cache import patch_vary_headers
from functools import wraps
from django.conf import settings

# Read cache settings from the environment
DISABLE_CACHE = getattr(
    settings, "DISABLE_CACHE", False
)

def cache_page_single(timeout, key_prefix=None):
    """
    Custom cache_page decorator that caches separate versions for authenticated and anonymous users.
    Allows disabling via an environment variable.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if DISABLE_CACHE:
                return view_func(request, *args, **kwargs)

            user_prefix = "auth" if request.user.is_authenticated else "anon"
            full_key_prefix = f"{key_prefix or 'default'}_{user_prefix}"
            
            response = cache_page(timeout, key_prefix=full_key_prefix)(view_func)(request, *args, **kwargs)
            patch_vary_headers(response, ['Cookie'])
            return response

        return _wrapped_view

    return decorator

def cache_page_slug(timeout, key_prefix=None):
    """
    Custom cache_page decorator that caches pages based on both the slug and authentication status.
    Allows disabling via an environment variable.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if DISABLE_CACHE:
                return view_func(request, *args, **kwargs)

            slug = kwargs.get("slug", "default")
            user_prefix = "auth" if request.user.is_authenticated else "anon"
            full_key_prefix = f"{key_prefix or 'default'}_{slug}_{user_prefix}"
            
            response = cache_page(timeout, key_prefix=full_key_prefix)(view_func)(request, *args, **kwargs)
            patch_vary_headers(response, ['Cookie'])
            return response

        return _wrapped_view

    return decorator


def cache_page_anonymous(timeout, key_prefix=None, consider_slug=False):
    """
    Cache pages only for anonymous users.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            full_key_prefix = key_prefix
            # Modify the key_prefix if consider_slug is True
            if consider_slug:
                slug = kwargs.get("slug", "default")
                full_key_prefix = f"{key_prefix}_{slug}" if key_prefix else slug

            # Apply caching without patching vary headers for anonymous users
            response = cache_page(timeout, key_prefix=full_key_prefix)(view_func)(request, *args, **kwargs)
            return response

        return _wrapped_view

    return decorator

