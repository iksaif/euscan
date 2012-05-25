from io import StringIO
from collections import defaultdict
import json

from gentoolkit import pprinter as pp
from portage.output import EOutput


class EOutputMem(EOutput):
    """
    Override of EOutput, allows to specify an output file for writes
    """
    def __init__(self, *args, **kwargs):
        super(EOutputMem, self).__init__(*args, **kwargs)
        self.out = StringIO()

    def getvalue(self):
        return self.out.getvalue()

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

    def get_formatted_output(self):
        data = {}

        for query in self.queries:
            data[query] = {
                "result": self.queries[query]["result"],
                "metadata": self.queries[query]["metadata"],
                "messages": self.queries[query]["output"].getvalue(),
            }

        if self.config["format"].lower() == "json":
            return json.dumps(data, indent=self.config["indent"])
        else:
            raise TypeError("Invalid output format")

    def result(self, cp, version, url, handler, confidence):
        from euscan.helpers import get_version_type

        if self.config['format']:
            _curr = self.queries[self.current_query]
            _curr["result"].append(
                {"version": version, "urls": [url], "handler": handler,
                 "confidence": confidence, "type": get_version_type(version)}
            )
        else:
            if not self.config['quiet']:
                print "Upstream Version:", pp.number("%s" % version),
                print pp.path(" %s" % url)
            else:
                print pp.cpv("%s-%s" % (cp, version)) + ":", pp.path(url)

    def metadata(self, key, value, show=True):
        if self.config["format"]:
            self.queries[self.current_query]["metadata"][key] = value
        elif show:
            print "%s: %s" % (key.capitalize(), value)

    def __getattr__(self, key):
        output = self.queries[self.current_query]["output"]
        return getattr(output, key)
