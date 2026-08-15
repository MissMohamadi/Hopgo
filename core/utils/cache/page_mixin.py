# utils/caching_mixin.py

from django.core.cache import cache
from django.views.generic import View
from django.http import HttpResponse


class CachePageMixin(View):
    """
    A reusable mixin for caching class-based views.
    Automatically includes request parameters and page in cache key.
    
    Usage:
        class MyView(CacheMixin, ListView):
            cache_timeout = 600
            cache_key_prefix = 'my_view'
            cache_exclude_params = ['q', 'search']  # Skip cache if these params have values
    """
    
    cache_timeout = 15 * 60
    cache_key_prefix = 'view_cache'
    cache_query_params = True
    cache_page_param = True
    cache_exclude_params = []  # Params that should bypass cache when they have values
    
    
    def get_request_params(self):
        """Get cleaned request GET parameters, excluding empty values"""
        params = {}
        for key, value in self.request.GET.items():
            # Only include params with actual values (not empty strings)
            if value and value.strip():
                params[key] = value
        return params
    
    def should_bypass_cache(self):
        """Check if request has any excluded parameters with values that should bypass cache"""
        if not self.cache_exclude_params:
            return False
        
        params = self.get_request_params()
        
        # Check if any excluded param has a non-empty value
        return any(param in self.cache_exclude_params and params.get(param) for param in self.cache_exclude_params)
    
    def get_cache_key(self):
        """Generate unique cache key based on view and request parameters"""
        key_parts = [self.cache_key_prefix, self.__class__.__name__]
        
        # Add primary key for detail views
        if hasattr(self, 'kwargs') and self.kwargs.get('slug'):
            key_parts.append(str(self.kwargs.get('slug')))
        elif hasattr(self, 'kwargs') and self.kwargs.get('pk'):
            key_parts.append(str(self.kwargs.get('pk')))
        
        # Add GET parameters (excluding empty values and excluded params)
        params = self.get_request_params()
        
        if self.cache_query_params and params:
            filtered_params = {
                key: value for key, value in params.items()
                if key not in self.cache_exclude_params
            }
            if filtered_params:
                param_parts = [f"{k}={v}" for k, v in sorted(filtered_params.items())]
                key_parts.append('&'.join(param_parts))
        
        # Add page parameter if enabled
        if self.cache_page_param:
            page = params.get('page', '1')
            key_parts.append(f"page_{page}")
        
        return '_'.join(key_parts)
    
    def get(self, request, *args, **kwargs):
        """Check cache before processing the view"""
        # Bypass cache if request has excluded parameters with values
        if self.should_bypass_cache():
            return super().get(request, *args, **kwargs)
        
        cache_key = self.get_cache_key()
        cached_content = cache.get(cache_key)
        
        if cached_content is not None:
            response = HttpResponse(cached_content)
            content_type = cache.get(f"{cache_key}_content_type")
            if content_type:
                response['Content-Type'] = content_type
            print("hit cache")
            return response
        
        # Process the view normally
        response = super().get(request, *args, **kwargs)
        
        # Cache the rendered content
        if response.status_code == 200 and hasattr(response, 'render'):
            response.render()
            cache.set(cache_key, response.content, self.cache_timeout)
            cache.set(f"{cache_key}_content_type", response.get('Content-Type'), self.cache_timeout)
        print("create cache")
        return response