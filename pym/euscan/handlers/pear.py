from euscan.handlers import php

HANDLER_NAME = "pear"
CONFIDENCE = 100
PRIORITY = 90


def can_handle(pkg, url=None):
    return url and url.startswith('http://%s.php.net/get/' % HANDLER_NAME)

scan_url = php.scan_url
scan_pkg = php.scan_pkg
