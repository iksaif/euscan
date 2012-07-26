import sys
from euscan import CONFIG, output
from euscan.handlers.package import handlers as pkg_handlers
from euscan.handlers.url import handlers as url_handlers


def find_best_pkg_handler(pkg):
    """
    Find the best handler for the given package
    """
    for handler in pkg_handlers:
        if handler.can_handle(pkg):
            return handler
    return None


def find_best_url_handler(pkg, url):
    """
    Find the best handler for the given url
    """
    for handler in url_handlers:
        if handler.can_handle(pkg, url):
            return handler
    return None


def scan(pkg, urls, on_progress=None):
    """
    Scans upstream for the given package.
    First tries if a package wide handler is available, then fallbacks
    in url handling.
    """
    pkg_handler = find_best_pkg_handler(pkg)
    if pkg_handler:
        if on_progress:
            on_progress(increment=35)

        if not CONFIG['quiet'] and not CONFIG['format']:
            sys.stdout.write("\n")

        versions = pkg_handler.scan(pkg)

        if on_progress:
            on_progress(increment=35)
        return versions

    if on_progress:
        progress_available = 70
        num_urls = sum([len(urls[fn]) for fn in urls])
        if num_urls > 0:
            progress_increment = progress_available / num_urls
        else:
            progress_increment = 0

    versions = []

    for filename in urls:
        for url in urls[filename]:
            if on_progress and progress_available > 0:
                on_progress(increment=progress_increment)
                progress_available -= progress_increment

            if not CONFIG['quiet'] and not CONFIG['format']:
                sys.stdout.write("\n")
            output.einfo("SRC_URI is '%s'" % url)

            if '://' not in url:
                output.einfo("Invalid url '%s'" % url)
                continue

            try:
                url_handler = find_best_url_handler(pkg, url)
                versions.extend(url_handler.scan(pkg, url))
            except Exception as e:
                output.ewarn(
                    "Handler failed: [%s] %s" %
                    (e.__class__.__name__, e.message)
                )

            if versions and CONFIG['oneshot']:
                break

    if on_progress and progress_available > 0:
        on_progress(increment=progress_available)

    return versions
