from django.template import Library
import math

register = Library()

# taken from http://lybniz2.sourceforge.net/safeeval.html
# make a list of safe functions
math_safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
                  'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp',
                  'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow',
                  'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']

# use the list to filter the local namespace
math_safe_dict = dict([(k, getattr(math, k)) for k in math_safe_list])

# add any needed builtins back in.
math_safe_dict['abs'] = abs


@register.filter('math')
def math_(lopr, expr):
    """Evals a math expression and returns it's value.

    "$1" is a placeholder. Insert "$1" in the expression where the value is
    to be used. All math functions such as abs, sin, cos, floor are supported.
    Example,
        a. You will be redirected in {{ seconds|math:"$1 / 60.0" }} minutes
        b. Square of {{ x }} is {{ x|math:"$1 * $1" }}
        c. Square root of {{ x }} is {{ x|math:"sqrt($1)" }}
        d. Given x = {{ x }}, (2 + x) * 6 = {{ x|math:"(2 + $1) * 6" }}
    """
    if lopr:
        return eval(expr.replace('$1', str(lopr)), {"__builtins__": None},
                    math_safe_dict)
    return ''
