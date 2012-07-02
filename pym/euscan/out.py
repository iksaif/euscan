from io import StringIO
from collections import defaultdict
import json
import signal
import time
import re

from gentoolkit import pprinter as pp
import portage
from portage.output import EOutput, TermProgressBar


class ProgressHandler(object):
    def __init__(self, progress_bar):
        self.curval = 0
        self.maxval = 0
        self.last_update = 0
        self.min_display_latency = 0.2
        self.progress_bar = progress_bar

    def on_progress(self, maxval=None, increment=1, label=None):
        self.maxval = maxval or self.maxval
        self.curval += increment

        if label:
            self.progress_bar.label(label)

        cur_time = time.time()
        if cur_time - self.last_update >= self.min_display_latency:
            self.last_update = cur_time
            self.display()

    def display(self):
        raise NotImplementedError(self)


def progress_bar():
    on_progress = None
    progress_bar = TermProgressBar()

    progress_handler = ProgressHandler(progress_bar)
    on_progress = progress_handler.on_progress

    def display():
        progress_bar.set(progress_handler.curval, progress_handler.maxval)
    progress_handler.display = display

    def sigwinch_handler(signum, frame):
        lines, progress_bar.term_columns = portage.output.get_term_size()
    signal.signal(signal.SIGWINCH, sigwinch_handler)

    yield on_progress

    # make sure the final progress is displayed
    progress_handler.display()
    signal.signal(signal.SIGWINCH, signal.SIG_DFL)

    yield None


def clean_colors(string):
    if type(string) is str:
        string = re.sub("\033\[[0-9;]+m", "", string)
        string = re.sub(r"\\u001b\[[0-9;]+m", "", string)
        string = re.sub(r"\x1b\[[0-9;]+m", "", string)
    return string


def to_mirror(url):
    mirrors = portage.settings.thirdpartymirrors()
    for mirror_name in mirrors:
        for mirror_url in mirrors[mirror_name]:
            if url.startswith(mirror_url):
                url_part = url.split(mirror_url)[1]
                return "mirror://%s%s%s" % (
                    mirror_name,
                    "" if url_part.startswith("/") else "/",
                    url_part
                )
    return url


class EOutputMem(EOutput):
    """
    Override of EOutput, allows to specify an output file for writes
    """
    def __init__(self, *args, **kwargs):
        super(EOutputMem, self).__init__(*args, **kwargs)
        self.out = StringIO()

    def getvalue(self):
        return clean_colors(self.out.getvalue())

    def _write(self, f, msg):
        super(EOutputMem, self)._write(self.out, msg)


class EuscanOutput(object):
    """
    Class that handles output for euscan
    """
    def __init__(self, config):
        self.config = config
        self.queries = defaultdict(dict)
        self.current_query = None

    def clean(self):
        self.queries = defaultdict(dict)
        self.current_query = None

    def set_query(self, query):
        self.current_query = query
        if query is None:
            return

        if query in self.queries:
            return

        if self.config["format"]:
            output = EOutputMem()
        else:
            output = EOutput()

        self.queries[query] = {
            "output": output,
            "result": [],
            "metadata": {},
        }

    def get_formatted_output(self, format_=None):
        data = {}

        for query in self.queries:
            data[query] = {
                "result": self.queries[query]["result"],
                "metadata": self.queries[query]["metadata"],
                "messages": self.queries[query]["output"].getvalue(),
            }

        format_ = format_ or self.config["format"]
        if format_.lower() == "json":
            return json.dumps(data, indent=self.config["indent"])
        elif format_.lower() == "dict":
            return data
        else:
            raise TypeError("Invalid output format")

    def result(self, cp, version, urls, handler, confidence):
        from euscan.helpers import get_version_type

        if self.config['format']:
            _curr = self.queries[self.current_query]
            _curr["result"].append(
                {
                    "version": version,
                    "urls": [to_mirror(url) if self.config['mirror'] else url
                             for url in urls.split()],
                    "handler": handler,
                    "confidence": confidence,
                    "type": get_version_type(version)
                }
            )
        else:
            if not self.config['quiet']:
                print "Upstream Version:", pp.number("%s" % version),
                print pp.path(" %s" % url)
            else:
                print pp.cpv("%s-%s" % (cp, version)) + ":", pp.path(url)

    def metadata(self, key, value, show=True):
        if self.config["format"]:
            self.queries[self.current_query]["metadata"][key] = \
                clean_colors(value)
        elif show:
            print "%s: %s" % (key.capitalize(), value)

    def __getattr__(self, key):
        if not self.config["quiet"] and self.current_query is not None:
            output = self.queries[self.current_query]["output"]
            return getattr(output, key)
        else:
            return lambda *x: None
