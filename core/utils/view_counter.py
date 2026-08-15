from django.db.models import F
from django.utils import timezone
from dateutil.parser import parse
from django.template.response import TemplateResponse

def count_views(session_key):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            if response.status_code == 200 and isinstance(response, TemplateResponse):
                obj = response.context_data.get("object")
                if not obj:
                    return response

                visited_objects = request.session.get(session_key, {})
                last_visit_time = visited_objects.get(str(obj.pk))

                if (
                    last_visit_time is None or
                    timezone.now() - parse(last_visit_time) > timezone.timedelta(hours=24)
                ):
                    visited_objects[str(obj.pk)] = timezone.now().isoformat()
                    request.session[session_key] = visited_objects

                    type(obj).objects.filter(pk=obj.pk).update(
                        views=F("views") + 1
                    )

            return response
        return wrapper
    return decorator
