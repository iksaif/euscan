from euscan.handlers.url import handlers
from euscan import output

PRIORITY = 100

HANDLER_NAME = "remote_id"
CONFIDENCE = 100.0


url_handlers = {handler.HANDLER_NAME: handler for handler in handlers}


def can_handle(pkg):
    # Return True if there's at least one remote-id that can be
    # handled by euscan
    try:
        remoteids = pkg.metadata.upstream()[0].upstream_remoteids()
    except IndexError:
        pass
    else:
        if len(remoteids) > 0:
            for remote_value, remote_type in remoteids:
                if remote_type in url_handlers:
                    return True
    return False


def scan(pkg):
    output.einfo("Using remote-id data")

    ret = []

    remoteids = pkg.metadata.upstream()[0].upstream_remoteids()
    for remote_value, remote_type in remoteids:
        if remote_type in url_handlers:
            remote_data = remote_value.split("/")
            scan_remote = getattr(
                url_handlers[remote_type], "scan_remote", None
            )
            if scan_remote:
                for url, pv in scan_remote(pkg, remote_data):
                    ret.append((url, pv, HANDLER_NAME, CONFIDENCE))
    return ret
