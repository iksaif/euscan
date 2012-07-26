"""
Package wide handlers for scanning upstream
"""

import pkgutil

handlers = []

# autoimport all modules in this directory and append them to handlers list
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    handlers.append(module)

# sort handlers by priority
handlers = sorted(
    handlers,
    key=lambda handler: handler.PRIORITY,
    reverse=True
)
