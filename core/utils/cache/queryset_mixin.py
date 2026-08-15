# utils/cache_mixin.py (simpler version)

import hashlib
from django.core.cache import cache


class CacheMixin:
    """
    Simple mixin to cache get_queryset or get_object results.
    """
    
    cache_timeout = 60 * 15
    cache_key_prefix = 'cache'
    cache_method = 'get_queryset'
    cache_vary_on_user = False
    cache_exclude_params = ['page']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original methods
        self._original_get_queryset = self.get_queryset
        self._original_get_object = self.get_object
    
    def _generate_cache_key(self):
        prefix = self.cache_key_prefix
        
        if self.cache_vary_on_user:
            if hasattr(self, 'request') and self.request.user.is_authenticated:
                prefix = f"{prefix}_user_{self.request.user.id}"
            else:
                prefix = f"{prefix}_anon"
        
        if hasattr(self, 'request') and self.request.GET:
            query_params = self.request.GET.urlencode()
            
            if self.cache_exclude_params:
                from urllib.parse import parse_qs, urlencode
                params = parse_qs(query_params)
                for param in self.cache_exclude_params:
                    params.pop(param, None)
                query_params = urlencode(params, doseq=True)
            
            if query_params:
                query_hash = hashlib.md5(query_params.encode()).hexdigest()[:8]
                prefix = f"{prefix}_{query_hash}"
        
        if self.cache_method == 'get_object' and hasattr(self, 'kwargs'):
            if 'slug' in self.kwargs:
                prefix = f"{prefix}_slug_{self.kwargs['slug']}"
            elif 'pk' in self.kwargs:
                prefix = f"{prefix}_pk_{self.kwargs['pk']}"
        
        return prefix
    
    def get_queryset(self):
        if self.cache_method != 'get_queryset':
            return self._original_get_queryset()
        
        cache_key = self._generate_cache_key()
        cached = cache.get(cache_key)
        
        if cached is not None:
            print(f"✅ CACHE HIT: {cache_key}")
            return cached
        
        print(f"❌ CACHE MISS: {cache_key}")
        
        # Call original method (which is your custom get_queryset)
        queryset = self._original_get_queryset()
        cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
    
    def get_object(self):
        if self.cache_method != 'get_object':
            return self._original_get_object()
        
        cache_key = self._generate_cache_key()
        cached = cache.get(cache_key)
        
        if cached is not None:
            print(f"✅ OBJECT CACHE HIT: {cache_key}")
            return cached
        
        print(f"❌ OBJECT CACHE MISS: {cache_key}")
        
        obj = self._original_get_object()
        cache.set(cache_key, obj, self.cache_timeout)
        
        return obj
    
    def invalidate_cache(self):
        cache.delete(self._generate_cache_key())