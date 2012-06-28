from euscan.handlers import generic

PRIORITY = 100

HANDLER_NAME = "kde"


def can_handle(cpv, url):
    if url.startswith('mirror://kde/'):
        return True
    return False


def clean_results(results):
    ret = []

    for path, version, confidence in results:
        if version == '5SUMS':
            continue
        ret.append((path, version, HANDLER_NAME, confidence))

    return ret


def scan(cpv, url):
    results = generic.scan(cpv, url)

    if url.startswith('mirror://kde/unstable/'):
        url = url.replace('mirror://kde/unstable/', 'mirror://kde/stable/')
        results += generic.scan(cpv, url)

    return clean_results(results)


def brute_force(cpv, url):
    results = generic.brute_force(cpv, url)

    if url.startswith('mirror://kde/unstable/'):
        url = url.replace('mirror://kde/unstable/', 'mirror://kde/stable/')
        results += generic.brute_force(cpv, url)

    return clean_results(results)
