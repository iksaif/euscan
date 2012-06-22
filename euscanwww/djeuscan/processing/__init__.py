class FakeLogger(object):
    def __getattr__(self, key):
        return lambda *x, **y: None
