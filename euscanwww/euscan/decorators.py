from django.db.models.query import QuerySet
from django.db.models import Model
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers

try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner


class DjangoJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return simplejson.loads(serializers.serialize('json', obj))
        if isinstance(obj, Model):
            # Must be iterable to be serilized
            obj = [obj]
            return simplejson.loads(serializers.serialize('json', obj))
        return simplejson.JSONEncoder.default(self, obj)

def render_to_json(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        output = function(request, *args, **kwargs)
        if not isinstance(output, dict):
            return output

        output = simplejson.dumps(output, cls=DjangoJSONEncoder)
        return HttpResponse(mimetype='application/json', content=output)
    return wrapper


