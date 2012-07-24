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


def find_best_handler(pkg, url):
    for handler in handlers:
        if handler.can_handle(pkg, url):
            return handler
    return None


def scan(pkg, url):
    handler = find_best_handler(pkg, url)
    if handler:
        return handler.scan(pkg, url)
    return []


def brute_force(pkg, url):
    handler = find_best_handler(pkg, url)
    if handler:
        return handler.brute_force(pkg, url)
    return []
