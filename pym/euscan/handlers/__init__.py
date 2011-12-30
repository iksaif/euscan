from euscan.handlers import generic, php, pypi, rubygem, kde

handlers = [ kde, php, pypi, rubygem, generic ]

def find_best_handler(cpv, url):
    for handler in handlers:
        if handler.can_handle(cpv, url):
            return handler
    return None

def scan(cpv, url):
    handler = find_best_handler(cpv, url)
    if handler:
        return handler.scan(cpv, url)
    return []

def brute_force(cpv, url):
    handler = find_best_handler(cpv, url)
    if handler:
        return handler.brute_force(cpv, url)
    return []
