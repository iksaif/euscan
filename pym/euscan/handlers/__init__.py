import pkgutil

# autoimport all modules in this directory and append them to handlers list
handlers = []
for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    handlers.append(module)

# sort handlers by priority (e.g.: generic should be run lastly)
handlers = sorted(
    handlers,
    key=lambda handler: handler.PRIORITY,
    reverse=True
)


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
