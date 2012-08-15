import re

import euscan.handlers


def apply_mangling_rule(mangle, string):
    # convert regex from perl format to python format
    # there are some regex in this format: s/pattern/replacement/
    m = re.match(r"s/(.*[^\\])/(.*)/", mangle)
    if not m:
        # or in this format s|pattern|replacement|
        m = re.match(r"s\|(.*[^\\])\|(.*)\|", mangle)
    if not m:  # Not a known regex format
        return string
    pattern, repl = m.groups()
    repl = re.sub(r"\$(\d+)", r"\\\1", repl)

    return re.sub(pattern, repl, string)


def apply_mangling_rules(kind, rules, string):
    """
    Apply multiple mangling rules (both sed-like and handlers)
    in order
    """

    if kind not in rules:
        return string

    for rule in rules[kind]:
        ret = None

        # First try handlers rules
        if rule == 'gentoo' and kind == 'versionmangle':
            ret = gentoo_mangle_version(string)
        elif kind == 'downloadurlmangle':
            ret = euscan.handlers.mangle_url(rule, string)
        elif kind == 'versionmangle':
            ret = euscan.handlers.mangle_version(rule, string)

        if ret is not None:  # Use return value as new string if not None
            string = ret
        else:  # Apply sed like rules
            string = apply_mangling_rule(rule, string)

    return string


def mangle_version(up_pv, options):
    # Default rule is gentoo when empty
    if 'versionmangle' not in options or not options['versionmangle']:
        options['versionmangle'] = ['gentoo']
    return apply_mangling_rules('versionmangle', options, up_pv)


def mangle_url(url, options):
    return apply_mangling_rules('downloadurlmangle', options, url)


# Stolen from g-pypi
def gentoo_mangle_version(up_pv):
    """Convert PV to MY_PV if needed

    :param up_pv: Upstream package version
    :type up_pv: string
    :returns: pv
    :rtype: string

    Can't determine PV from upstream's version.
    Do our best with some well-known versioning schemes:

    * 1.0a1 (1.0_alpha1)
    * 1.0-a1 (1.0_alpha1)
    * 1.0b1 (1.0_beta1)
    * 1.0-b1 (1.0_beta1)
    * 1.0-r1234 (1.0_pre1234)
    * 1.0dev-r1234 (1.0_pre1234)
    * 1.0.dev-r1234 (1.0_pre1234)
    * 1.0dev-20091118 (1.0_pre20091118)

    Regex match.groups():
    * pkgfoo-1.0.dev-r1234
    * group 1 pv major (1.0)
    * group 2 replace this with portage suffix (.dev-r)
    * group 3 suffix version (1234)

    The order of the regexes is significant. For instance if you have
    .dev-r123, dev-r123 and -r123 you should order your regex's in
    that order.

    The chronological portage release versions are:

    * _alpha
    * _beta
    * _pre
    * _rc
    * release
    * _p

    **Example:**

    >>> gentoo_mangle_version('1.0b2')
        '1.0_beta2'

    .. note::
    The number of regex's could have been reduced, but we use four
    number of match.groups every time to simplify the code

    """
    bad_suffixes = re.compile(
        r'((?:[._-]*)(?:dev|devel|final|stable|snapshot)$)', re.I)
    revision_suffixes = re.compile(
        r'(.*?)([\._-]*(?:r|patch|p)[\._-]*)([0-9]*)$', re.I)
    suf_matches = {
        '_pre': [
            r'(.*?)([\._-]*dev[\._-]*r?)([0-9]+)$',
            r'(.*?)([\._-]*(?:pre|preview)[\._-]*)([0-9]*)$',
            ],
        '_alpha': [
            r'(.*?)([\._-]*(?:alpha|test)[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*a[\._-]*)([0-9]*)$',
            r'(.*[^a-z])(a)([0-9]*)$',
            ],
        '_beta': [
            r'(.*?)([\._-]*beta[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*b)([0-9]*)$',
            r'(.*[^a-z])(b)([0-9]*)$',
            ],
        '_rc': [
            r'(.*?)([\._-]*rc[\._-]*)([0-9]*)$',
            r'(.*?)([\._-]*c[\._-]*)([0-9]*)$',
            r'(.*[^a-z])(c[\._-]*)([0-9]+)$',
            ],
    }
    rs_match = None
    pv = up_pv
    additional_version = ""

    rev_match = revision_suffixes.search(up_pv)
    if rev_match:
        pv = up_pv = rev_match.group(1)
        replace_me = rev_match.group(2)
        rev = rev_match.group(3)
        additional_version = '_p' + rev

    for this_suf in suf_matches.keys():
        if rs_match:
            break
        for regex in suf_matches[this_suf]:
            rsuffix_regex = re.compile(regex, re.I)
            rs_match = rsuffix_regex.match(up_pv)
            if rs_match:
                portage_suffix = this_suf
                break

    if rs_match:
        # e.g. 1.0.dev-r1234
        major_ver = rs_match.group(1)  # 1.0
        replace_me = rs_match.group(2)  # .dev-r
        rev = rs_match.group(3)  # 1234
        pv = major_ver + portage_suffix + rev
    else:
        # Single suffixes with no numeric component are simply removed.
        match = bad_suffixes.search(up_pv)
        if match:
            suffix = match.groups()[0]
            pv = up_pv[: - (len(suffix))]

    pv = pv + additional_version

    return pv
