import os, sys
import pkgutil

from euscan import CONFIG, output
import euscan.mangling

from gentoolkit.metadata import MetaData

handlers = {'package' : [], 'url' : [], 'all' : {}}

# autoimport all modules in this directory and append them to handlers list
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    if not hasattr(module, 'HANDLER_NAME'):
        continue
    if hasattr(module, 'scan_url'):
        handlers['url'].append(module)
    if hasattr(module, 'scan_pkg'):
        handlers['package'].append(module)
    handlers['all'][module.HANDLER_NAME] = module

# sort handlers by priority
def sort_handlers(handlers):
    return sorted(
        handlers,
        key=lambda handler: handler.PRIORITY,
        reverse=True
    )

handlers['package'] = sort_handlers(handlers['package'])
handlers['url'] = sort_handlers(handlers['url'])

def find_best_handler(kind, pkg, *args):
    """
    Find the best handler for the given package
    """
    for handler in handlers[kind]:
        if handler.can_handle(pkg, *args):
            return handler
    return None

def find_handlers(kind, names):
    ret = []

    for name in names:
        # Does this handler exist, and handle this kind of thing ? (pkg / url)
        if name in handlers['all'] and handlers['all'][name] in handlers[kind]:
            ret.append(handlers['all'][name])

    return ret

def get_metadata(pkg):
    metadata = {}

    pkg_metadata = None

    meta_override = os.path.join('metadata', pkg.category, pkg.name, 'metadata.xml')

    try:
        if os.path.exists(meta_override):
            pkg_metadata = MetaData(meta_override)
            output.einfo('Using custom metadata: %s' % meta_override)
        if not pkg_metadata:
            pkg_metadata = pkg.metadata
    except Exception, e:
        output.ewarn('Error when fetching metadata: %s' % str(e))

    if not pkg_metadata:
        return {}

    # Support multiple remote-id and multiple watch
    for upstream in pkg_metadata._xml_tree.findall("upstream"):
        for node in upstream.findall("watch"):
            options = dict(node.attrib)
            options['data'] = node.text

            if "type" in options:
                handler = options['type']
            else:
                handler = "url"
                options['type'] = "url"

            for key in ["versionmangle", "downloadurlmangle"]:
                value = options.get(key, None)
                if value:
                    options[key] = value.split(";")

            if handler not in metadata:
                metadata[handler] = []
            metadata[handler].append(options)

    for upstream in pkg_metadata._xml_tree.findall("upstream"):
        for node in upstream.findall("remote-id"):
            handler = node.attrib.get("type")
            if not handler:
                continue
            if handler in metadata:
                for i in range(len(metadata[handler])):
                    if not metadata[handler][i]['data']:
                        metadata[handler][i]['data'] = node.text
            else:
                metadata[handler] = [{'type' : handler, 'data' : node.text }]

    return metadata

def scan_pkg(pkg_handler, pkg, options, on_progress=None):
    versions = []

    if on_progress:
        on_progress(increment=35)

    for o in options:
        versions += pkg_handler.scan_pkg(pkg, o)

    if on_progress:
        on_progress(increment=35)

    return versions

def scan_url(pkg, urls, options, on_progress=None):
    versions = []

    if on_progress:
        progress_available = 70
        num_urls = sum([len(urls[fn]) for fn in urls])
        if num_urls > 0:
            progress_increment = progress_available / num_urls
        else:
            progress_increment = 0

    for filename in urls:
        for url in urls[filename]:
            if on_progress and progress_available > 0:
                on_progress(increment=progress_increment)
                progress_available -= progress_increment

            output.einfo("SRC_URI is '%s'" % url)

            if '://' not in url:
                output.einfo("Invalid url '%s'" % url)
                continue

            try:
                url_handler = find_best_handler('url', pkg, url)
                for o in options:
                    versions += url_handler.scan_url(pkg, url, o)
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

def scan(pkg, urls, on_progress=None):
    """
    Scans upstream for the given package.
    First tries if a package wide handler is available, then fallbacks
    in url handling.
    """

    if not CONFIG['quiet'] and not CONFIG['format']:
        sys.stdout.write('\n')

    metadata = get_metadata(pkg)
    versions = []

    pkg_handlers = find_handlers('package', metadata.keys())
    if not pkg_handlers:
        pkg_handler = find_best_handler('package', pkg)
        if pkg_handler: pkg_handlers = [pkg_handler]

    for pkg_handler in pkg_handlers:
        options = metadata.get(pkg_handler.HANDLER_NAME, [{}])
        versions += scan_pkg(pkg_handler, pkg, options, on_progress)

    if not pkg_handlers:
        versions += scan_url(pkg, urls, [{}], on_progress)

    return versions

def mangle(kind, name, string):
    if name not in handlers['all']:
        return None
    handler = handlers['all'][name]
    if not hasattr(handler, 'mangle_%s' % kind):
        return None
    return getattr(handler, 'mangle_%s' % kind)(string)

def mangle_url(name, string):
    return mangle('url', name, string)

def mangle_version(name, string):
    return mangle('version', name, string)
