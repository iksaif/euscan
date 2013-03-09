import re

gentoo_unstable = ("alpha", "beta", "pre", "rc")
gentoo_types = ("alpha", "beta", "pre", "rc", "p")


def is_version_type_stable(version_type):
    return version_type not in gentoo_unstable


def is_version_stable(version):
    return is_version_type_stable(get_version_type(version))


def get_version_type(version):
    types = []

    if "9999" in version or "99999999" in version:
        return "live"

    for token in re.findall("[\._-]([a-zA-Z]+)", version):
        if token in gentoo_types:
            types.append(token)
    if types:
        return types[0]  # TODO: consider returning all types
    return "release"

# Stolen from pkg_resources, but importing it is not a good idea

component_re = re.compile(r'(\d+ | [a-z]+ | \.| -)', re.VERBOSE)
replace = \
    {'pre': 'c', 'preview': 'c', '-': 'final-', 'rc': 'c', 'dev': '@'}.get


def _parse_version_parts(s):
    for part in component_re.split(s):
        part = replace(part, part)
        if not part or part == '.':
            continue
        if part[:1] in '0123456789':
            yield part.zfill(8)    # pad for numeric comparison
        else:
            yield '*' + part

    yield '*final'  # ensure that alpha/beta/candidate are before final


def parse_version(s):
    """Convert a version string to a chronologically-sortable key

    This is a rough cross between distutils' StrictVersion and LooseVersion;
    if you give it versions that would work with StrictVersion, then it behaves
    the same; otherwise it acts like a slightly-smarter LooseVersion. It is
    *possible* to create pathological version coding schemes that will fool
    this parser, but they should be very rare in practice.

    The returned value will be a tuple of strings.  Numeric portions of the
    version are padded to 8 digits so they will compare numerically, but
    without relying on how numbers compare relative to strings.  Dots are
    dropped, but dashes are retained.  Trailing zeros between alpha segments
    or dashes are suppressed, so that e.g. "2.4.0" is considered the same as
    "2.4". Alphanumeric parts are lower-cased.

    The algorithm assumes that strings like "-" and any alpha string that
    alphabetically follows "final"  represents a "patch level".  So, "2.4-1"
    is assumed to be a branch or patch of "2.4", and therefore "2.4.1" is
    considered newer than "2.4-1", which in turn is newer than "2.4".

    Strings like "a", "b", "c", "alpha", "beta", "candidate" and so on (that
    come before "final" alphabetically) are assumed to be pre-release versions,
    so that the version "2.4" is considered newer than "2.4a1".

    Finally, to handle miscellaneous cases, the strings "pre", "preview", and
    "rc" are treated as if they were "c", i.e. as though they were release
    candidates, and therefore are not as new as a version string that does not
    contain them, and "dev" is replaced with an '@' so that it sorts lower than
    than any other pre-release tag.
    """
    parts = []
    for part in _parse_version_parts(s.lower()):
        if part.startswith('*'):
            if part < '*final':  # remove '-' before a prerelease tag
                while parts and parts[-1] == '*final-':
                    parts.pop()
            # remove trailing zeros from each series of numeric parts
            while parts and parts[-1] == '00000000':
                parts.pop()
        parts.append(part)
    return tuple(parts)
