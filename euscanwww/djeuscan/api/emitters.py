from piston.emitters import Emitter, XMLEmitter

class EuscanXMLEmitter(XMLEmitter):
    _parent = []
    _known_parents = {
        'vlog' : 'version',
        'herds' : 'herd',
        'maintainers' : 'maintainer',
        'packaged' : 'version',
        'upstream' : 'version',
        'packages' : 'package',
        'categories' : 'category'
        }

    def _push_parent(self, parent):
        self._parent.append(parent)

    def _pop_parent(self):
        if self._parent:
            return self._parent.pop()
        else:
            return None

    def _current_parent(self):
        if self._parent:
            return self._parent[-1]
        else:
            return None

    def _name_from_parent(self):
        return self._known_parents.get(self._current_parent(), 'resource')

    def _to_xml(self, xml, data):
        def recurse(name, xml, item):
            attrs = {}
            xml.startElement(name, attrs)
            self._push_parent(name)
            self._to_xml(xml, item)
            self._pop_parent()
            xml.endElement(name)

        if isinstance(data, (list, tuple)):
            for item in data:
                name = self._name_from_parent()
                recurse(name, xml, item)
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                recurse(key, xml, value)
        else:
            super(EuscanXMLEmitter, self)._to_xml(xml, data)
