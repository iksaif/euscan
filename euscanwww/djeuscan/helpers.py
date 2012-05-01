"""
djeuscan.helpers
"""


def xint(i):
    try:
        return int(i)
    except Exception:
        return 0
