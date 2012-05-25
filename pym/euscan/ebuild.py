import os
import sys
import imp

import portage
from portage.const import VDB_PATH
from portage import _encodings
from portage import _shell_quote
from portage import _unicode_decode
from portage import _unicode_encode


# Stolen from the ebuild command
def package_from_ebuild(ebuild):
    pf = None
    if ebuild.endswith(".ebuild"):
        pf = os.path.basename(ebuild)[:-7]
    else:
        return False

    if not os.path.isabs(ebuild):
        mycwd = os.getcwd()
        # Try to get the non-canonical path from the PWD evironment variable,
        # since the canonical path returned from os.getcwd() may may be
        # unusable in cases where the directory stucture is built from
        # symlinks.
        pwd = os.environ.get('PWD', '')
        if sys.hexversion < 0x3000000:
            pwd = _unicode_decode(pwd, encoding=_encodings['content'],
                                  errors='strict')
        if pwd and pwd != mycwd and \
            os.path.realpath(pwd) == mycwd:
            mycwd = portage.normalize_path(pwd)
        ebuild = os.path.join(mycwd, ebuild)

    ebuild = portage.normalize_path(ebuild)
    # portdbapi uses the canonical path for the base of the portage tree, but
    # subdirectories of the base can be built from symlinks (like crossdev
    # does).
    ebuild_portdir = os.path.realpath(
      os.path.dirname(os.path.dirname(os.path.dirname(ebuild))))
    ebuild = os.path.join(ebuild_portdir, *ebuild.split(os.path.sep)[-3:])
    vdb_path = os.path.join(portage.settings['ROOT'], VDB_PATH)

    # Make sure that portdb.findname() returns the correct ebuild.
    if ebuild_portdir != vdb_path and \
        ebuild_portdir not in portage.portdb.porttrees:
        if sys.hexversion >= 0x3000000:
            os.environ["PORTDIR_OVERLAY"] = \
                os.environ.get("PORTDIR_OVERLAY", "") + \
                " " + _shell_quote(ebuild_portdir)
        else:
            os.environ["PORTDIR_OVERLAY"] = \
                os.environ.get("PORTDIR_OVERLAY", "") + \
                " " + _unicode_encode(_shell_quote(ebuild_portdir),
                encoding=_encodings['content'], errors='strict')

        portage.close_portdbapi_caches()
        imp.reload(portage)
    del portage.portdb.porttrees[1:]
    if ebuild_portdir != portage.portdb.porttree_root:
        portage.portdb.porttrees.append(ebuild_portdir)

    if not os.path.exists(ebuild):
        return False

    ebuild_split = ebuild.split("/")
    cpv = "%s/%s" % (ebuild_split[-3], pf)

    if not portage.catpkgsplit(cpv):
        return False

    if ebuild.startswith(os.path.join(portage.root, portage.const.VDB_PATH)):
        mytree = "vartree"

        portage_ebuild = portage.db[portage.root][mytree].dbapi.findname(cpv)

        if os.path.realpath(portage_ebuild) != ebuild:
            return False

    else:
        mytree = "porttree"

        portage_ebuild = portage.portdb.findname(cpv)

        if not portage_ebuild or portage_ebuild != ebuild:
            return False

    return cpv
