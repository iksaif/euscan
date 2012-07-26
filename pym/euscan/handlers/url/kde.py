from euscan.handlers.url import generic

PRIORITY = 90

HANDLER_NAME = "kde"


def can_handle(pkg, url):
    if url.startswith('mirror://kde/'):
        return True
    return False


def clean_results(results):
    ret = []

    for path, version, _, confidence in results:
        if version == '5SUMS':
            continue
        ret.append((path, version, HANDLER_NAME, confidence))

    return ret


def scan(pkg, url):
    results = generic.scan(pkg.cpv, url)

    if url.startswith('mirror://kde/unstable/'):
        url = url.replace('mirror://kde/unstable/', 'mirror://kde/stable/')
        results += generic.scan(pkg.cpv, url)

    if not results:  # if nothing was found go brute forcing
        results = generic.brute_force(pkg.cpv, url)

        if url.startswith('mirror://kde/unstable/'):
            url = url.replace('mirror://kde/unstable/', 'mirror://kde/stable/')
            results += generic.brute_force(pkg.cpv, url)

    return clean_results(results)
